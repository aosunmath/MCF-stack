# Comments

Comments are disabled in MCF-stack. The build omits comment links, panels, scripts, and the comments page while `comments.json` has `enabled` set to `false`. No inherited discussion threads or giscus repository/category IDs are used.

When comments are requested, configure Discussions and giscus for `aosunmath/MCF-stack`, then populate `comments.json` with this repository’s `repo_id`, `category`, `category_id`, and `category_slug`, and set `enabled` to `true`. Keep `repo` set to the fork and `term_prefix` set to `MCF-stack: Special Solutions of Mean Curvature Flow`. Do not reuse another repository’s identifiers.
