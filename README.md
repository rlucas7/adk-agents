# ADK is configured to look for an api key in
`GOOGLE_API_KEY` env var

# quick new agent setup
`adk create`

# run the agent
`adk run <agent-name>`

# pip installs
`pip install google-adk[eval] wikipedia arxiv`

# The research agent has several tools

## Tools:
  - wikipedia search tool
  - arxiv search tool
  - google search tool
  - report writing tool

## evals
Run via:
```sh
adk eval \
    <AGENT_MODULE_FILE_PATH> \
    <EVAL_SET_ID> \
    [--config_file_path=<PATH_TO_CONFIG_FILE>] \
    [--print_detailed_results]
```
Example, run from top level directory:
```sh
adk eval research_assistant/ ra_eval_set_v1 \
    --config_file_path research_assistant/eval_config.json \
    --print_detailed_results
```
