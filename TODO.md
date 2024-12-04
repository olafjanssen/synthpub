# SynthPub TODO

## API

- [x] Add Id to Topic model
- [x] Add Article model and store in db
- [x] Refactor the code so the API is more modular
- [x] Add list of feed urls to Topic model
- [x] Add update topic article to route based on feed urls
- [x] Add refined articles also in db
- [x] Keep a link to a previous version of an article
- [x] Create separate topic files instead of having everything in one json file
- [x] Store in the topic file a list of feed urls that have been used to update the article, and include a hash of the content of the article so we know when it has been updated
- [x] Make sure the article does not update using already processed feed items
- [x] Add a source feed to the article model
- [x] Refactor the code so that almost no logic is in the routes, but mostly in the curator package
- [x] Use the initial generator to only create a structure, not content
- [x] Add a project model that contains a list of topics
- [x] Make the trigger API call async

## Connectors

- [x] Create a file system connector
- [ ] Create a Exchange email connector
- [ ] Create a (gmail) email connector
- [ ] Create a MS Teams connector
- [x] Create a Youtube transcript connector

## AI Curator

- [x] Allow for different LLM providers such as Ollama and OpenAI
- [x] Add a relevance filter
- [ ] Add a substance extractor
- [ ] Add a scheduler that will update the topics every X hours

## Publisher

- [ ] Create a function to publish the topics to a file system location

## Front-end

- [x] Create a simple front-end for the API
- [x] Add a page for a list of topics
- [x] Create navigation to previous versions of an article
- [x] Create navigation to next version of an article
- [x] Add a list of sources at the bottom of the article
- [x] Add a page or modal to edit a topic
- [x] Styling update towards dpbtse.com
- [ ] Add a projects list page
- [ ] Create a artice page version that shows the origin of each part of the article similar to git blame.

## Desktop

- [x] Create a desktop wrapper app using Pywebview and Pyinstaller
- [ ] Update the styling to reflect a desktop app more