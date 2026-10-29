## In five minutes

AI can draft a reply to a sales enquiry. Permission to send a price to a customer is a separate matter. For a first business trial, our suggestion is to separate drafting from execution: the system prepares the material; a person checks the recipient, amount and attachments. Start with one activity and measure correction time too. A quickly written wrong email is still a wrong email.

This issue draws on documentation from three vendors. We have not compared the tools in live operation for this sample and claim no measured time savings.

## Put approval before the action

**What is documented.** Power Automate offers “Start and wait for an approval”, which waits for the approver’s response. n8n describes human review of individual AI-agent tools: denying a request prevents that action from running. [Microsoft](https://learn.microsoft.com/en-us/power-automate/get-started-approvals), [n8n](https://docs.n8n.io/build/integrate-ai/ai-examples/human-in-the-loop-for-tools.md)

**Our interpretation.** An enquiry workflow can be designed in two parts. One extracts the requirements and prepares a draft. The other may send an email only after review. A similar gate can be required before writing to a CRM, the system holding customer records. An approval button alone does not prove the workflow has been connected correctly.

**What to check.** Does the review show the exact recipient, full text, amount and attachments? Does sending stop after a rejection and when nobody responds? Is there another route through which the agent can send without approval? Product documentation cannot answer these questions about your particular setup.

## A business plan is not blanket permission to upload data

**What is documented.** OpenAI states that it does not use business data to train its models by default; explicitly opting in to data sharing can be an exception. That commitment does not mean data is never processed or stored. [OpenAI](https://openai.com/enterprise-privacy/)

**Our interpretation.** Before uploading an actual enquiry, identify what it contains. A public product catalogue, an unpublished price list and a customer’s personal details are different things. A demonstration can use a fictional business and a fabricated document containing no real contacts or trade secrets.

**What to check.** Which account and plan is the employee using? Which connected applications receive the content? Who can access the result, and how long is it retained? This is not a finding about the legal permissibility of your processing; that depends on the particular data and terms.

## A small test that does not swallow the week

The following is an **editorial proposal**, not a completed benchmark. Choose ten fictional enquiries. Ten is the proposed trial size, not statistical proof of reliability. Include a clear request, a missing deadline, an unknown price and a document that is difficult to read.

For each case, record:

- preparation time using the usual method;
- preparation time with AI, including review and corrections;
- errors in the recipient, amount, deadline and attachments;
- whether the system acknowledged missing information;
- whether a rejected or unanswered request actually prevented sending.

Calculate savings as the difference between the two total times. If the system drafts quickly but review takes longer than the original work, there is no saving. If results are good only for tidy documents, limit the intended use accordingly. Ten cases are not a reason to release the system unsupervised on every customer.

## What to take to the next meeting

One page with four answers: which activity is being tried, who is responsible for review, where the process stops and how the benefit will be measured. Another licence can wait until you know which problem it needs to solve.

At the next review, watch measured correction time, recurring errors and what happened to rejected actions. Even a polished draft cannot rescue an automation that sends a different file from the one a person just approved.
