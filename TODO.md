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
- [x] Allow for different LLM providers such as Ollama and OpenAI
- [x] Store in the topic file a list of feed urls that have been used to update the article, and include a hash of the content of the article so we know when it has been updated
- [ ] Make sure the article does not update using already processed feed items
- [ ] Add a source feed to the article model
- [ ] Refactor the code so that almost no logic is in the routes, but mostly in the curator package

## Front-end

- [x] Create a simple front-end for the API
- [x] Add a page for a list of topics
- [x] Create navigation to previous versions of an article
- [x] Create navigation to next version of an article
- [ ] Add a page for a list of articles

