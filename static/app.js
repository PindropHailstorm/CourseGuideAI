document.addEventListener("DOMContentLoaded", () => {
    const chatForm = document.getElementById("chat-form");
    const questionInput = document.getElementById("question");
    const messagesDiv = document.getElementById("messages");
    const clearBtn = document.getElementById("clear");
    const compareBtn = document.getElementById("compare");
    const comparisonDiv = document.getElementById("comparison");

    let currentLastQuery = "";

    document.body.addEventListener("click", (e) => {
        const btn = e.target.closest("[data-q]");
        if (btn) {
            questionInput.value = btn.getAttribute("data-q");
            handleSend();
        }
    });

    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        handleSend();
    });

    questionInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });

    clearBtn.addEventListener("click", () => {
        messagesDiv.innerHTML = `
            <div class="message assistant">
                <div class="avatar">✦</div>
                <div class="bubble">
                    <b>Chat Reset.</b>
                    <p>Ask a new question about South Asian University courses, prerequisites, or policies.</p>
                </div>
            </div>`;
        resetInspector();
    });

    compareBtn.addEventListener("click", () => {
        if (!currentLastQuery) return;
        comparisonDiv.classList.remove("hidden");
        comparisonDiv.innerHTML = "<em>Querying Statistical LLM Baseline...</em>";

        fetch("/api/compare", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: currentLastQuery })
        })
        .then(res => res.json())
        .then(data => {
            comparisonDiv.innerHTML = `
                <strong>Baseline LLM Response:</strong><br>${data.llm_answer}<br><br>
                ${data.tradeoff_discussion.replace(/\n/g, '<br>')}
            `;
        })
        .catch(err => {
            comparisonDiv.innerHTML = "Error fetching benchmark comparison.";
        });
    });

    function handleSend() {
        const queryText = questionInput.value.trim();
        if (!queryText) return;

        currentLastQuery = queryText;
        questionInput.value = "";

        appendMessage("user", queryText);

        const track = document.getElementById("studentTrack").value;
        const checkboxes = document.querySelectorAll(".course-checkbox:checked");
        const completedCourses = Array.from(checkboxes).map(cb => cb.value);

        document.getElementById("stage-input").innerText = `"${queryText}"`;
        document.getElementById("state-input").innerText = "COMPLETED";
        document.getElementById("state-input").className = "stage-state completed";

        fetch("/api/query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                student_id: "s101",
                track: track,
                completed_courses: completedCourses,
                query: queryText
            })
        })
        .then(res => res.json())
        .then(data => {
            updateInspector(data);
            appendMessage("assistant", data.answer);
        })
        .catch(err => {
            appendMessage("assistant", "System Error connecting to SWI-Prolog Engine.");
        });
    }

    function appendMessage(role, text) {
        const msgDiv = document.createElement("div");
        msgDiv.className = `message ${role}`;
        
        const avatar = role === "user" ? "👤" : "✦";
        msgDiv.innerHTML = `
            <div class="avatar">${avatar}</div>
            <div class="bubble">${text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}</div>
        `;
        messagesDiv.appendChild(msgDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    function updateInspector(data) {
        const stages = data.stages || {};

        if (stages.nlp) {
            document.getElementById("stage-nlp").innerText = stages.nlp.description;
            document.getElementById("state-nlp").innerText = stages.nlp.status;
            document.getElementById("state-nlp").className = "stage-state completed";
        }

        if (stages.ambiguity) {
            document.getElementById("stage-ambiguity").innerText = stages.ambiguity.description;
            const st = stages.ambiguity.status === "NEEDS_CLARIFICATION" ? "CLARIFY" : "COMPLETED";
            document.getElementById("state-ambiguity").innerText = st;
            document.getElementById("state-ambiguity").className = `stage-state ${st.toLowerCase()}`;
        }

        const conf = data.confidence || 0.0;
        document.getElementById("confidence-value").innerText = `${(conf * 100).toFixed(0)}%`;
        document.getElementById("confidence-meter").style.width = `${conf * 100}%`;

        if (stages.reasoning) {
            document.getElementById("stage-reasoning").innerText = stages.reasoning.description;
            const rState = stages.reasoning.status === "SKIPPED" ? "SKIPPED" : "COMPLETED";
            document.getElementById("state-reasoning").innerText = rState;
            document.getElementById("state-reasoning").className = `stage-state ${rState.toLowerCase()}`;
        }

        const traceOl = document.getElementById("trace");
        traceOl.innerHTML = "";
        if (data.trace && data.trace.length > 0) {
            data.trace.forEach(step => {
                const li = document.createElement("li");
                li.innerText = step;
                traceOl.appendChild(li);
            });
        } else {
            traceOl.innerHTML = "<li>No trace steps available.</li>";
        }
    }

    function resetInspector() {
        document.getElementById("stage-input").innerText = "Waiting for a question...";
        document.getElementById("state-input").innerText = "READY";
        document.getElementById("state-input").className = "stage-state";

        document.getElementById("stage-nlp").innerText = "Intent and entity slot matching will appear here.";
        document.getElementById("state-nlp").innerText = "WAITING";
        document.getElementById("state-nlp").className = "stage-state";

        document.getElementById("stage-ambiguity").innerText = "Verifies query specification before logic execution.";
        document.getElementById("state-ambiguity").innerText = "WAITING";
        document.getElementById("state-ambiguity").className = "stage-state";

        document.getElementById("stage-reasoning").innerText = "PySwip execution trace over Horn clauses.";
        document.getElementById("state-reasoning").innerText = "WAITING";
        document.getElementById("state-reasoning").className = "stage-state";

        document.getElementById("confidence-value").innerText = "—";
        document.getElementById("confidence-meter").style.width = "0%";
        document.getElementById("trace").innerHTML = "<li>Submit a question to see the trace.</li>";
        comparisonDiv.classList.add("hidden");
    }
});
