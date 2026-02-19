/**
 * @name Complete struct field layouts
 * @kind problem
 * @problem.severity info
 * @id cpp/linux/all-struct-fields
 * @description Lists every field in every non-zero-size struct with type,
 *              offset, and size info. Useful for understanding memory layout.
 * @tags kernel structures
 */

import cpp

from Struct t, Field field
where
  t.getSize() != 0 and
  field = t.getAField()
select field,
  t.getName() + "." + field.getName() + " (type=" + field.getType().toString() + " offset=" +
    field.getByteOffset().toString() + " size=" + field.getType().getSize().toString() + ")"
