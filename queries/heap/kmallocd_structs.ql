/**
 * @name Structs allocated via kmalloc with slab info
 * @kind problem
 * @problem.severity info
 * @id cpp/linux/kmallocd-structs
 * @description Finds all structs allocated via kmalloc and maps them to
 *              their SLUB slab cache. Useful for heap layout analysis.
 * @tags security kernel heap
 */

import cpp
import lib.KernelSlab

from
  FunctionCall f, AssignExpr a, Initializer i, DeclarationEntry d, PointerType p, Struct s
where
  f.getTarget().hasName("kmalloc") and
  (
    i = f.getParent() and
    d = i.getDeclaration().getADeclarationEntry() and
    p = d.getType()
    or
    a = f.getParent() and p = a.getType()
  ) and
  s = p.getBaseType().getUnspecifiedType()
select f,
  s.getName() + " (size=" + s.getSize().toString() + " slab=" + kmallocSlab(s.getSize()) + ")"
