/**
 * @name All non-zero struct sizes
 * @kind problem
 * @problem.severity info
 * @id cpp/linux/all-struct-sizes
 * @description Lists all structs with non-zero size and their definition
 *              locations. Useful for mapping the kernel type landscape.
 * @tags kernel structures
 */

import cpp

from Struct t, int size
where size = t.getSize() and size != 0
select t, t.getName() + " (size=" + size.toString() + ")"
