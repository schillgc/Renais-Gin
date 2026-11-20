(() => {
  "use strict";

  const demo = {
    bottles: [],
    pledges: [],
    nextPledgeNumber: 1,
  };

  const bottleForm = document.querySelector("#bottle-form");
  const bottleFields = document.querySelector("#bottle-demo-fields");
  const bottleSelect = document.querySelector("#bottle-id");
  const registeredBottles = document.querySelector("#registered-bottles");
  const bottleCountLabel = document.querySelector("#bottle-count-label");
  const pledgeForm = document.querySelector("#pledge-form");
  const pledgeFields = document.querySelector("#pledge-demo-fields");
  const pledgeLocked = document.querySelector("#pledge-locked");
  const pledgeBottleSelect = document.querySelector("#pledge-bottle");
  const pledgeText = document.querySelector("#pledge-text");
  const pledgeLength = document.querySelector("#pledge-length");
  const pledgeList = document.querySelector("#pledge-list");
  const statusMessage = document.querySelector("#demo-status");

  const demoIds = new Set(["RG-DEMO-001", "RG-DEMO-002", "RG-DEMO-003"]);
  const reviewers = ["Demo reviewer 1", "Demo reviewer 2", "Demo reviewer 3"];
  const impactLabels = {
    community: "Community",
    environmental: "Environment",
    education: "Education",
    other: "Other",
  };

  function setStatus(message) {
    statusMessage.textContent = message;
  }

  function makeElement(tag, className, content) {
    const element = document.createElement(tag);
    if (className) {
      element.className = className;
    }
    if (content !== undefined) {
      element.textContent = content;
    }
    return element;
  }

  function updateMetrics() {
    document.querySelector("#metric-bottles").textContent = String(demo.bottles.length);
    document.querySelector("#metric-pledges").textContent = String(demo.pledges.length);
    document.querySelector("#metric-votes").textContent = String(
      demo.pledges.reduce((total, pledge) => total + pledge.votes.length, 0)
    );
    bottleCountLabel.textContent = String(demo.bottles.length);
  }

  function renderBottles() {
    bottleFields.disabled = false;
    pledgeFields.disabled = demo.bottles.length === 0;
    registeredBottles.replaceChildren();

    if (demo.bottles.length === 0) {
      registeredBottles.append(makeElement("li", "empty-row", "No sample bottles registered yet."));
    } else {
      demo.bottles.forEach((bottleId) => {
        const row = makeElement("li");
        const id = makeElement("code", "", bottleId);
        const label = makeElement("span", "", "Registered in this demo");
        row.append(id, label);
        registeredBottles.append(row);
      });
    }

    Array.from(bottleSelect.options).forEach((option) => {
      if (option.value) {
        option.disabled = demo.bottles.includes(option.value);
      }
    });

    pledgeBottleSelect.replaceChildren();
    demo.bottles.forEach((bottleId) => {
      const option = document.createElement("option");
      option.value = bottleId;
      option.textContent = bottleId;
      pledgeBottleSelect.append(option);
    });

    pledgeLocked.hidden = demo.bottles.length > 0;
    pledgeForm.hidden = demo.bottles.length === 0;
    updateMetrics();
  }

  function pledgeStatus(pledge) {
    const approvals = pledge.votes.filter((vote) => vote.approval).length;
    const rejections = pledge.votes.length - approvals;
    if (approvals >= 3) {
      return { label: "Approved in demo", kind: "approved", closed: true };
    }
    if (rejections >= 3) {
      return { label: "Rejected in demo", kind: "rejected", closed: true };
    }
    if (pledge.votes.length >= reviewers.length) {
      return { label: "No consensus in demo", kind: "closed", closed: true };
    }
    return { label: "Needs review", kind: "", closed: false };
  }

  function renderPledges() {
    pledgeList.replaceChildren();

    if (demo.pledges.length === 0) {
      const empty = makeElement("div", "empty-activity");
      empty.append(
        makeElement("span", "empty-symbol", "—"),
        makeElement("p", "", "Your demo pledges will appear here.")
      );
      pledgeList.append(empty);
      updateMetrics();
      return;
    }

    demo.pledges.forEach((pledge) => {
      const card = makeElement("article", "pledge-item");
      const details = makeElement("div");
      const status = pledgeStatus(pledge);
      const statusPill = makeElement("span", `status-pill${status.kind ? ` is-${status.kind}` : ""}`, status.label);
      const title = makeElement("h4", "", pledge.bottleId);
      const promise = makeElement("p", "", pledge.text);
      const plan = makeElement("p", "", `Plan: ${pledge.plan}`);
      const meta = makeElement("div", "pledge-item-meta");
      const focus = makeElement("span", "meta-chip", impactLabels[pledge.impactType]);
      meta.append(focus, makeElement("span", "meta-chip", "Browser-only sample"));

      const approvals = pledge.votes.filter((vote) => vote.approval).length;
      const rejections = pledge.votes.length - approvals;
      const voteCount = makeElement("div", "vote-count");
      voteCount.append(
        makeElement("span", "", `Simulated approvals: ${approvals}`),
        makeElement("span", "", `Simulated rejections: ${rejections}`)
      );

      details.append(statusPill, title, promise, plan, meta, voteCount);

      const actions = makeElement("div", "vote-actions");
      const approveButton = makeElement("button", "", "Simulate approval");
      const rejectButton = makeElement("button", "", "Simulate rejection");
      const limit = makeElement("span", "vote-limit", `${pledge.votes.length} / ${reviewers.length} demo votes`);
      approveButton.type = "button";
      rejectButton.type = "button";
      approveButton.disabled = status.closed;
      rejectButton.disabled = status.closed;
      approveButton.addEventListener("click", () => castDemoVote(pledge.id, true));
      rejectButton.addEventListener("click", () => castDemoVote(pledge.id, false));
      actions.append(approveButton, rejectButton, limit);

      card.append(details, actions);
      pledgeList.append(card);
    });

    updateMetrics();
  }

  function castDemoVote(pledgeId, approval) {
    const pledge = demo.pledges.find((item) => item.id === pledgeId);
    if (!pledge || pledgeStatus(pledge).closed) {
      return;
    }

    const reviewer = reviewers[pledge.votes.length];
    pledge.votes.push({ reviewer, approval });
    const state = pledgeStatus(pledge);
    renderPledges();
    setStatus(`${reviewer} cast a simulated ${approval ? "approval" : "rejection"}. Status: ${state.label.toLowerCase()}.`);
  }

  bottleForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const bottleId = bottleSelect.value;

    if (!demoIds.has(bottleId) || demo.bottles.includes(bottleId)) {
      setStatus("Choose an available sample bottle ID.");
      return;
    }

    demo.bottles.push(bottleId);
    bottleForm.reset();
    renderBottles();
    setStatus(`${bottleId} was added to this browser-only demo.`);
  });

  pledgeText.addEventListener("input", () => {
    pledgeLength.textContent = `${pledgeText.value.length} / 500`;
  });

  pledgeForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const formData = new FormData(pledgeForm);
    const bottleId = String(formData.get("bottleId"));

    if (!demo.bottles.includes(bottleId)) {
      setStatus("Register a sample bottle before adding a pledge.");
      return;
    }
    if (demo.pledges.some((pledge) => pledge.bottleId === bottleId)) {
      setStatus("This demo allows one pledge per sample bottle. Register another bottle to try again.");
      return;
    }

    const pledge = {
      id: demo.nextPledgeNumber,
      bottleId,
      text: String(formData.get("pledgeText")).trim(),
      plan: String(formData.get("impactPlan")).trim(),
      impactType: String(formData.get("impactType")),
      votes: [],
    };

    demo.nextPledgeNumber += 1;
    demo.pledges.push(pledge);
    pledgeForm.reset();
    pledgeLength.textContent = "0 / 500";
    renderPledges();
    setStatus("Pledge added to this page's memory. It was not submitted to a real review service.");
  });

  document.querySelector("#reset-demo").addEventListener("click", () => {
    demo.bottles = [];
    demo.pledges = [];
    demo.nextPledgeNumber = 1;
    bottleForm.reset();
    pledgeForm.reset();
    pledgeLength.textContent = "0 / 500";
    renderBottles();
    renderPledges();
    setStatus("Demo reset. No data had been saved.");
  });

  renderBottles();
  renderPledges();
})();
