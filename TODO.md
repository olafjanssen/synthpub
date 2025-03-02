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
- [x] Create an in-memory cache for the topics
- [x] Make the feed system more generic
- [x] Create an endpoint for application settings
- [ ] Create an endpoint for project settings

## Connectors

- [x] Create a RSS feed connector
- [x] Create a general web page connector
- [x] Create a file system connector
- [x] Create a (gmail) email connector
- [x] Create a Youtube transcript connector
- [x] Create an Arxiv connector
- [ ] Create a general scientific paper connector
- [ ] Create a MS Teams connector
- [ ] Create a Exchange email connector

## AI Curator

- [x] Allow for different LLM providers such as Ollama and OpenAI
- [x] Give prompts proper topic title and description
- [x] Add a relevance filter
- [ ] Add a substance extractor
- [ ] Extract knowledge graph information from the article
- [x] Add a scheduler that will update the topics every X hours
- [ ] Add relevance reason to topic source feed
- [x] Add Mistral LLM provider
- [ ] Compute substance score or information density per article
- [ ] Keep track of the LLM calls and token usage

## Transformer

- [x] Create a transformer architecture for transforming the article into other formats
- [ ] Create a Markdown transformer with front-matter
- [x] Create an mp3 transformer
- [x] Create a podcast transformer

## Publisher

- [x] Create a function to publish the articles to a file system location
- [x] Create a function to publish the articles as a podcast
- [x] Create a function to publish the articles to a GitLab repository
- [ ] Create a function to publish the articles to a GitHub repository

## Front-end

- [x] Create a simple front-end for the API
- [x] Add a page for a list of topics
- [x] Create navigation to previous versions of an article
- [x] Create navigation to next version of an article
- [x] Add a list of sources at the bottom of the article
- [x] Add a page or modal to edit a topic
- [x] Styling update towards dpbtse.com
- [x] Add a projects list page
- [ ] Create a article page version that shows the origin of each part of the article similar to git blame.
- [ ] Show outline of the article on the left
- [ ] Show article changes on the right
- [ ] Show only relevant sources for the article version (not all sources)
- [ ] Show an update feed on the main page
- [ ] Create a sidebar to chat with the application
- [x] Add a application settings page
- [x] Add all environment variables to the application settings page
- [x] Add LLM options to the application settings page
- [ ] Add a project settings page/modal

## Desktop

- [x] Create a desktop wrapper app using Pywebview and Pyinstaller
- [x] Update the styling to reflect a desktop app more
- [x] Apply compact card design idea
- [ ] Adjust the window title to that of the project/article
- [ ] Add a system tray icon and option
- [x] Allow for opening a new folder as database

