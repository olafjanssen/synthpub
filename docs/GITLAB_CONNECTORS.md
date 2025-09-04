# GitLab Feed Connectors

This document describes the GitLab feed connectors that allow SynthPub to process commit updates and issue list updates from GitLab groups and individual repositories.

## Overview

Two new feed connectors have been added to support GitLab integration:

1. **GitLabGroupConnector** - Processes all projects within a GitLab group
2. **GitLabRepoConnector** - Processes a specific GitLab repository

## URL Format

Both connectors use a custom `gitlab://` URL scheme:

- **Group URLs**: `gitlab://host/group-name` or `gitlab://host/group/subgroup`
- **Repository URLs**: `gitlab://host/group/project` or `gitlab://host/group/subgroup/project`

### Examples

```
# GitLab.com (public)
gitlab://gitlab.com/gitlab-org
gitlab://gitlab.com/gitlab-org/gitlab

# Custom GitLab instance
gitlab://gitlab.example.com/my-company
gitlab://gitlab.example.com/my-company/my-project

# Subgroups
gitlab://gitlab.com/group/subgroup
gitlab://gitlab.com/group/subgroup/project
```

## Configuration

### Environment Variables

Set the `GITLAB_TOKEN` environment variable with your GitLab access token:

```bash
export GITLAB_TOKEN="your-gitlab-access-token"
```

### Required Token Scopes

The GitLab token needs the following scopes:
- `read_api` - For accessing commits and issues
- `read_repository` - For commit details

## Connector Details

### GitLabGroupConnector

**Purpose**: Fetches commits and issues from all projects within a GitLab group.

**URL Pattern**: `gitlab://host/group-name` or `gitlab://host/group/subgroup`

**Features**:
- Processes all projects in the group
- Includes projects from subgroups
- Fetches recent commits (last 7 days)
- Fetches recent issues (last 7 days)
- Caches data for 1 hour

**Content Format**:
- **Commits**: Author, date, message, commit ID, full diff, and project context
- **Issues**: Title, description, author, state, labels, issue number, discussions/comments, and project context

### GitLabRepoConnector

**Purpose**: Fetches commits and issues from a specific GitLab repository.

**URL Pattern**: `gitlab://host/group/project` or `gitlab://host/group/subgroup/project`

**Features**:
- Processes a single repository
- Fetches recent commits (last 7 days)
- Fetches recent issues (last 7 days)
- Caches data for 30 minutes

**Content Format**: Same as GitLabGroupConnector

## Usage

### Adding GitLab Feeds

1. **Group Feed**: Add a topic with URL `gitlab://gitlab.com/your-group`
2. **Repository Feed**: Add a topic with URL `gitlab://gitlab.com/your-group/your-project`

### Content Processing

The connectors return structured content that includes:

- **URL**: Direct link to the commit or issue
- **Content**: Full formatted text with complete details including:
  - **Commits**: Full commit message, author, date, commit ID, and complete diff showing all file changes
  - **Issues**: Full title, description, author, state, labels, issue number, and all discussions/comments
- **Title**: Full commit message or issue title (no truncation)
- **Type**: Either "commit" or "issue"
- **Project**: Project name for context
- **Author**: Author of the commit or issue
- **Date**: Creation/commit date

### Filtering

The connectors automatically filter out:
- Merge commits (commits starting with "Merge branch")
- Empty or irrelevant content

## Implementation Details

### Files Created

- `src/news/feeds/gitlab_utils.py` - Shared utilities for GitLab API operations
- `src/news/feeds/gitlab_group.py` - Group connector implementation
- `src/news/feeds/gitlab_repo.py` - Repository connector implementation
- `src/news/feeds/__init__.py` - Updated to include new connectors

### API Integration

The connectors use GitLab's REST API v4:
- `/groups/:id/projects` - List group projects
- `/projects/:id/repository/commits` - List project commits
- `/projects/:id/repository/commits/:sha` - Get detailed commit information
- `/projects/:id/repository/commits/:sha/diff` - Get commit diff
- `/projects/:id/issues` - List project issues
- `/projects/:id/issues/:issue_iid` - Get detailed issue information
- `/projects/:id/issues/:issue_iid/discussions` - Get issue discussions/comments

### Error Handling

- Graceful handling of API errors
- Logging of failed requests
- Fallback to empty results on errors

### Caching

- Group data cached for 1 hour
- Repository data cached for 30 minutes
- Uses the existing cache system

## Troubleshooting

### Common Issues

1. **Missing Token**: Ensure `GITLAB_TOKEN` environment variable is set
2. **Insufficient Permissions**: Verify token has required scopes
3. **Invalid URL Format**: Use correct `gitlab://` scheme
4. **Network Issues**: Check connectivity to GitLab instance

### Debugging

Enable debug logging to see detailed information about:
- URL parsing
- API requests
- Content processing
- Error conditions

## Examples

### Group Monitoring

Monitor all projects in a GitLab group:

```
URL: gitlab://gitlab.com/my-company
Result: Commits and issues from all projects in my-company group
```

### Repository Monitoring

Monitor a specific repository:

```
URL: gitlab://gitlab.com/my-company/my-project
Result: Commits and issues from my-project repository only
```

### Custom GitLab Instance

Monitor projects on a self-hosted GitLab:

```
URL: gitlab://gitlab.company.com/internal-projects
Result: Commits and issues from internal-projects group
```

## Future Enhancements

Potential improvements for future versions:

1. **Merge Request Support**: Add support for merge requests
2. **Custom Time Ranges**: Allow configurable time ranges for fetching
3. **Project Filtering**: Add options to exclude specific projects
4. **Webhook Integration**: Real-time updates via GitLab webhooks
5. **Advanced Filtering**: More sophisticated content filtering options
