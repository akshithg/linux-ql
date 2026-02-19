/**
 * @name ifdef CONFIG blocks in source
 * @kind problem
 * @problem.severity info
 * @id cpp/linux/ifdef-configs
 * @description Detects #ifdef CONFIG_* preprocessor blocks, mapping each
 *              to its source file and line range.
 * @tags kernel structures
 */

import cpp

from PreprocessorBranch p
where p.toString().matches("%CONFIG%")
select p,
  p.getLocation().getFile().toString() + ":" + p.getLocation().getStartLine().toString() + "-" +
    p.getNext().getLocation().getStartLine().toString()
