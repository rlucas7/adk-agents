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


## Agents in the repo

Currently there are:

- research_assistant
- cal_agent

The `cal_agent` works on localhost only. This is because of the need to
run through the oauth2 protocol for accessing google calendar and making
edits. The oauth2 workflow is in testing mode and I am the person on
the list of testers.

The `research_assistant` is deployed into a public cloud run function.
The DNS entry is the default one for the google cloud app so it's not
a nice, memorable url but it works. Still improvements to do on the
app though.
