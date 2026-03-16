## this dockerfile is for the research_assistant agent

FROM python:3.11-slim
WORKDIR /app

# Create a non-root user
RUN adduser --disabled-password --gecos "" myuser

# Switch to the non-root user
USER myuser

# Set up environment variables - Start
ENV PATH="/home/myuser/.local/bin:$PATH"

ENV GOOGLE_GENAI_USE_VERTEXAI=1
ENV GOOGLE_CLOUD_PROJECT=adk-agent-study-490218
ENV GOOGLE_CLOUD_LOCATION=us-central1

# Set up environment variables - End

# Install ADK and other python dependencies
RUN pip install google-adk==1.27.1 wikipedia arxiv
# Install ADK - End

# Copy agent - Start

# Set permission
COPY --chown=myuser:myuser "agents/research_assistant/" "/app/agents/research_assistant/"

# Copy agent - End

# Install Agent Deps - Start
# No requirements.txt.
# Install Agent Deps - End

EXPOSE 8000

CMD adk web --port=8000 --host=0.0.0.0 --session_service_uri=memory:// --artifact_service_uri=memory://     "/app/agents"

