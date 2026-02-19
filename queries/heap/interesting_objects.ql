/**
 * @name Interesting objects for kernel heap exploitation
 * @kind problem
 * @problem.severity warning
 * @id cpp/linux/interesting-objects
 * @description Finds kmalloc'd structs with size, GFP flags, and flexible
 *              array member info — useful for heap exploitation research.
 * @tags security kernel heap
 */

import cpp
import lib.KernelAlloc

from KmallocCall kfc, Struct s
where
  s = kfc.getStruct() and
  not kfc.getSizeArg().isAffectedByMacro()
select kfc,
  "kmalloc of " + s.getName() + " (size=" + kfc.getSize() + " flags=" + kfc.getFlag() +
    " flexible=" + kfc.isFlexible() + ")"
