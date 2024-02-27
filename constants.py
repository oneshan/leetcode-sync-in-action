# GraphQL Query String

SUBMISSION_DETAIL_QUERY = '''
    query submissionDetails($submissionId: Int!) {
      submissionDetails(submissionId: $submissionId) {
        runtimePercentile
        memoryPercentile
      }
'''

PROBLEMSET_QUESTION_LIST_QUERY = '''
    query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
      problemsetQuestionList: questionList(
        categorySlug: $categorySlug
        limit: $limit
        skip: $skip
        filters: $filters
      ) {
        total: totalNum
        questions: data {
          questionId
          content
          hints
          difficulty
          frontendQuestionId: questionFrontendId
          paidOnly: isPaidOnly
          status
          title
          titleSlug
          topicTags {
            name
            id
            slug
          }
        }
      }
    }
'''


QUESTION_SUBMISSIONS_QUERY = '''
    query submissionList(
      $offset: Int!
      $limit: Int!
      $lastKey: String
      $questionSlug: String!
      $lang: Int
      $status: Int
    ) {
      questionSubmissionList(
        offset: $offset
        limit: $limit
        lastKey: $lastKey
        questionSlug: $questionSlug
        lang: $lang
        status: $status
      ) {
        lastKey
        hasNext
        submissions {
          id
          title
          titleSlug
          status
          statusDisplay
          lang
          langName
          runtime
          timestamp
          url
          memory
          notes
        }
      }
    }
'''

QUESTION_INFO_QUERY = '''
    query questionInfo($titleSlug: String!) {
        question(titleSlug: $titleSlug) {
            questionId
            title
            titleSlug
            difficulty
            content
            hints
            status
            note
            topicTags {
                name
                slug
            }
        }
    }
'''

# Constant

LANG_MAPPING = {
    'bash': { 'file_format': 'sh', 'comment_syntax': '#' },
    'c': { 'file_format': 'c', 'comment_syntax': '//' },
    'cpp': { 'file_format': 'cpp', 'comment_syntax': '//' },
    'csharp': { 'file_format': 'cs', 'comment_syntax': '//' },
    'elixir': { 'file_format': 'ex', 'comment_syntax': '#' },
    'erlang': { 'file_format': 'erl', 'comment_syntax': '%' },
    'golang': { 'file_format': 'go', 'comment_syntax': '//' },
    'java': { 'file_format': 'java', 'comment_syntax': '//' },
    'javascript': { 'file_format': 'js', 'comment_syntax': '//' },
    'kotlin': { 'file_format': 'kt', 'comment_syntax': '//' },
    'php': { 'file_format': 'php', 'comment_syntax': '//' },
    'python': { 'file_format': 'py', 'comment_syntax': '#' },
    'python3': { 'file_format': 'py', 'comment_syntax': '#' },
    'racket': { 'file_format': 'rkt', 'comment_syntax': ';' },
    'ruby': { 'file_format': 'rb', 'comment_syntax': '#' },
    'rust': { 'file_format': 'rs', 'comment_syntax': '//' },
    'scala': { 'file_format': 'scala', 'comment_syntax': '//' },
    'swift': { 'file_format': 'swift', 'comment_syntax': '//' },
    'typescript': { 'file_format': 'ts', 'comment_syntax': '//' },
}

# Default Template

PATH = "problems/{{ '%04d' % question_id }}.{{ title_slug }}"
SOLUTION_FILENAME = 'solution_{{ id }}.{{ file_format }}'

SOLUTION_CONTENT = '''{{ comment_syntax }} {{ '%04d' % question_id }} - {{ title }}
{{ comment_syntax }} Date: {{ dt.strftime('%Y-%m-%d') }}
{{ comment_syntax }} Runtime: {{ runtime }}, Memory: {{ memory }}
{{ comment_syntax }} Submission Id: {{ id }}


{{ code }}
'''

README_CONTENT = '''# {{ '%04d' % question_id }} - {{ title }}

## Metadata

 - Difficulty: `{{ difficulty }}`
 - Link: https://www.leetcode.com/problems/{{ title_slug }}

## Content

{{ content }}

## Hint

{% for hint in hints %}- {{ hint }}
{% endfor %}

'''
