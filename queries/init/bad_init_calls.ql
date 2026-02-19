/**
 * @name Cross-section calls to __init functions
 * @kind problem
 * @problem.severity warning
 * @id cpp/linux/bad-init-calls
 * @description Finds non-__init functions that call __init-annotated
 *              functions. After boot, __init memory is freed — calling
 *              into it causes use-after-free or undefined behavior.
 * @tags security kernel init
 */

import cpp
import lib.KernelFunc

from KernelFunc func, KernelFunc caller, FunctionCall call
where
  (func.isInSection(".init.text") or func.isInSection(".head.text")) and
  call = func.getACallToThisFunction() and
  caller = call.getEnclosingFunction() and
  not caller.isInline() and
  not caller.isInSection(".init.text") and
  not caller.isInSection(".ref.text") and
  not caller.isInSection(".head.text")
select call,
  caller.getName() + " calls __init function " + func.getName()
