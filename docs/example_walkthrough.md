Example Walkthrough

This document shows the tool running against real regulatory text and a mock vendor's paperwork, with the actual documents and findings used as the demo case.

The setup

Regulation: An excerpt of Consumer Financial Protection Bureau (CFPB) guidance on complaint handling, covering four requirements: a 15-day acknowledgment window, written record-keeping, a 60-day escalation notice, and non-retaliation.

Vendor: A mock cloud data vendor ("NimbusCloud"), represented by two documents — their services contract with the client bank, and their public privacy and data handling policy.

What the tool found

Running gap coverage and contradiction checking against these documents produced 3 gaps and 1 contradiction.

Gap 1: Complaint Acknowledgment Timeline — Medium severity

Verdict: Gap Found

Regulation requires:

"Institutions shall acknowledge receipt of a written complaint within 15 business days."

Vendor's document says:

"Vendor shall forward any customer complaints received regarding Client's services to Client within 5 business days of receipt."

In plain terms: The regulation requires the customer to get an acknowledgment within 15 days. The contract only promises the vendor will pass the complaint along internally within 5 days — that's a different commitment, and it doesn't actually guarantee the customer hears back in time.

Gap 2: Complaint Record-Keeping — Low severity

Verdict: Gap Found

Regulation requires:

"Institutions must maintain a written record of each complaint received, including the date of receipt, the nature of the complaint, and the resolution provided to the consumer."

Vendor's document says:

"No relevant sentence found — the contract's complaint-handling clause covers forwarding only, with no mention of record-keeping."

In plain terms: The regulation requires a written log of every complaint. The contract says nothing about keeping any kind of record, so there's no evidence this requirement is being met at all.

Gap 3: 60-Day Escalation Notice — High severity

Verdict: Gap Found

Regulation requires:

"If a complaint cannot be resolved within 60 days, the institution must provide the consumer with a written explanation of the delay and an estimated timeline for resolution."

Vendor's document says:

"No relevant sentence found — the contract has no clause addressing complaints that remain unresolved past any deadline."

In plain terms: This is a real, undisputed gap — the contract has no provision at all for what happens if a complaint drags on. A customer with an unresolved issue after 60 days would have no contractual guarantee of even being told why.

Contradiction: Data Encryption — High severity

Verdict: Contradiction Found

Contract says:

"Vendor shall encrypt all Client customer data at rest and in transit using industry-standard encryption protocols (AES-256 or equivalent)."

Privacy policy says:

"Data may be temporarily cached in unencrypted form during processing to optimize system performance."

In plain terms: The contract promises data is always encrypted, with no exceptions stated. The privacy policy openly admits there's at least one case — temporary caching — where it isn't. These two statements can't both be fully true at the same time, which is exactly the kind of inconsistency a reviewer would want flagged before signing off on this vendor.

Why this demonstrates the core idea

Gap coverage and contradiction checking answer two different questions about the same vendor:

Gap coverage asks: does this vendor's paperwork actually satisfy the law?
Contradiction checking asks: does this vendor's paperwork agree with itself?

A vendor could theoretically pass every regulation check and still have documents that contradict each other, as the encryption example shows — legal compliance and internal consistency are separate risks, and this tool checks for both.

Every finding above is backed by an exact quoted sentence from the source text, separated from the plain-language explanation. That separation matters: the quote is the evidence, the explanation is the interpretation — a reviewer can check the quote against the original document directly, rather than trusting an AI-generated summary at face value.

Iteration note

An earlier version of this tool returned only a verdict and a paraphrased explanation, blended together in one paragraph. This version asks the model to quote the exact sentence responsible for each finding as a separate field, so the evidence and the interpretation are no longer mixed — a meaningful improvement for a compliance tool, where "trust me" isn't good enough.

Known limitations, honestly noted
Chunking by character count, not by sentence or paragraph, occasionally cuts text mid-sentence. This hasn't changed the meaning of any finding so far, but it's a rough edge worth polishing.
Exact quoting is a harder task for a small model. The tool asks for word-for-word quotes, and a 3B-parameter local model can occasionally paraphrase slightly instead of quoting exactly. When a quote doesn't match the source text precisely, the UI falls back to showing the full excerpt without highlighting, rather than failing.
The model used throughout this demo is small, free, and runs entirely locally (Llama 3.2, 3B parameters, via Ollama), so the whole project runs at zero cost. The architecture is built so swapping in a stronger model (e.g. Claude) is a one-line change — which would likely improve both quote accuracy and the subtlety of gaps or contradictions it can catch.