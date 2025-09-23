# Evaluation Strategy

1. **Job Relevance** – Compare ranked job list against manually curated opportunities from IIT Kanpur faculty labs. Calculate precision@5 and recall metrics.
2. **Communication Quality** – Use rubric (clarity, professionalism, personalization) scored by human reviewers on a 1-5 scale. Target average score ≥4.
3. **ATS Improvements** – Benchmark ATS scores of baseline resumes vs. tailored variants using third-party ATS testers; target ≥15% improvement.
4. **Live Pilots** – Conduct end-to-end submissions to IIT Kanpur faculty research postings, measure response rates, and track interview conversions.
5. **Observability** – Capture Prometheus metrics (jobs fetched, emails sent, review pauses) and monitor errors via Sentry dashboards.
