if (interactive()) {
    require(conflicted)

    conflict_prefer("filter", "dplyr")
    conflict_prefer("lag", "dplyr")
    conflict_prefer("select", "dplyr")
    conflict_prefer("margins", "margins")
    conflict_prefer("View", "utils")

    # leave this out so I write fewer bugs:
    # conflict_prefer("get", "base")

    # I want to see garbage collection
    # gcinfo(TRUE)
}

#if (requireNamespace("rlang", quietly = TRUE)) {
#  options(error = rlang::entrace)
#}
