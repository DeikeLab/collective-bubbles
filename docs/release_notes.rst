Release notes
=============

v0.3
----
* Improve data storing and parameters exporting:

  * HDF5, parameters are stored as table attributes, starting with `params`
  * CSV, parameters are stored in a header tagger `<params>` to `</params>`

* Start building documentation (hosted on readthedocs)

v0.2.1
------

* Erase and replace v0.2 (newly added versioning was buggy).
* More efficient data saving (no need to store 230 in `int64` structure).
* Implement `SimuC`, where bubbles burst after a certain constant time.

v0.1
----

* First public release of CoBubbles
* Contains already the data structure and simulations run in 
