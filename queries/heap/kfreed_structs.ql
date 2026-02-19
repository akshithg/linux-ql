/**
 * @name Structs freed via kfree with slab info
 * @kind problem
 * @problem.severity info
 * @id cpp/linux/kfreed-structs
 * @description Finds all structs passed to kfree and maps them to their
 *              SLUB slab cache. Useful for use-after-free analysis.
 * @tags security kernel heap
 */

import cpp
import lib.KernelSlab

from FunctionCall f, PointerType p, Struct s
where
  f.getTarget().hasName("kfree") and
  p = f.getArgument(0).getType() and
  s = p.getBaseType().getUnspecifiedType()
select f,
  s.getName() + " (size=" + s.getSize().toString() + " slab=" + kmallocSlab(s.getSize()) + ")"
