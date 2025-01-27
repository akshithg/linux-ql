/**
 * @name ifdef CONFIG blocks in source
 * @kind problem
 * @problem.severity info
 * @id cpp/ifdef-configs
 * @description Detects ifdef CONFIG blocks in source code.
 */

import cpp

from
    PreprocessorBranch p
where
    p.toString().matches("%CONFIG%")
select
    p,
    p.getLocation().getFile().toString(),
    p.getLocation().getStartLine(),
    p.getNext().getLocation().getStartLine()
