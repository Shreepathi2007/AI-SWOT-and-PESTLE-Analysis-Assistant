# AI SWOT and PESTLE Analysis Assistant

## Status
Approved by the user for implementation.

## Goal
Build a student-friendly local web application that accepts a business or project description and produces an editable SWOT and PESTLE analysis. The application must be transparent that its local/demo analysis uses rules and keyword-based suggestions, not a hosted generative AI model.

## Technology
- Backend: Python with Flask.
- Frontend: HTML, CSS, vanilla JavaScript, and Bootstrap.
- Database: SQLite for saved analysis history.
- Authentication: None.
- External AI provider: None; no API key or external service is required.

## User experience
- Provide a responsive form for a business/project name, industry, and description.
- Validate required inputs and show clear errors.
- Generate structured Strengths, Weaknesses, Opportunities, Threats, and Political, Economic, Social, Technological, Legal, and Environmental factors.
- Let users edit generated analysis sections before saving.
- Save analyses locally and provide history viewing, copy, and text-download actions.
- Include a concise explanation that generated content is a starting point and should be reviewed.

## Architecture and data
- Serve the frontend and JSON endpoints from Flask.
- Use a small, deterministic local analysis service that derives suggestions from the submitted text and domain-oriented prompt cues.
- Persist analysis records in SQLite, including the input fields, structured analysis, and timestamps.
- Keep secrets and external service configuration out of the application because no provider integration is in scope.

## Acceptance criteria
- The application starts locally with documented setup instructions.
- A user can submit a description, receive all ten SWOT/PESTLE categories, edit the results, and save them.
- Saved analyses can be listed and reopened after restarting the application.
- Input validation and API errors are visible to the user.
- The UI is responsive and uses Bootstrap with project-specific CSS.
