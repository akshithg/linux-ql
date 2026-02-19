/**
 * @name Freed structs containing function pointers
 * @kind problem
 * @problem.severity warning
 * @id cpp/linux/kfreed-structs-with-func-ptrs
 * @description Finds kfree'd structs that contain function pointers
 *              (directly or nested). These are prime targets for UAF
 *              exploitation to hijack control flow.
 * @tags security kernel heap
 */

import cpp
import lib.KernelSlab

/**
 * Recursively finds function pointer types within a struct,
 * including those nested in embedded struct fields.
 */
FunctionPointerType anyFuncPtr(Struct s) {
  result = s.getAField().getUnspecifiedType()
  or
  result = anyFuncPtr(s.getAField().getUnspecifiedType())
}

from FunctionCall f, PointerType p, FunctionPointerType fp, Struct s
where
  f.getTarget().hasName("kfree") and
  p = f.getArgument(0).getType() and
  s = p.getBaseType().getUnspecifiedType() and
  fp = anyFuncPtr(s)
select s,
  s.getName() + " (size=" + s.getSize().toString() + " slab=" + kmallocSlab(s.getSize()) +
    ") has function pointer"
