fritzchecksum
=============

Small pip installable module and Windows GUI (32 & 64 bits) to calculate the
CRC of an AVM's Fritz!Box configuration file.

The command line/gui versions allow to overwrite the CRC directly in the read
file or save it to a new file.

Installation
------------

  - *GUI* (look in **Releases** for the latest zip files)

    The *zip* files contain standalone versions that need no installation. Any
    settings/paths will be saved to the ``ini`` file in the same directory.

    Simply unpack and run

  - *Command Line* and *module*

    Simply run::

       pip install fritzchecksum

    The command line utility is also named ``fritzchecksum``


Command Line Utility
--------------------

The usage is as follows::

  $ fritzchecksum --help
  usage: fritzchecksum-script.py [-h] [--change | --output OUTPUT] input

  FritzChecksum Calculator/Overwriter

  positional arguments:
    input                 Write input to output with new CRC

  optional arguments:
    -h, --help            show this help message and exit
    --change, -c          Change CRC directly in input file
    --output OUTPUT, -o OUTPUT
                          Write input to output with new CRC


Module *fritzchecksum*
----------------------

In your code do things like::

  import fritzchecksum

  ...
  ...

  myexport = open('myexportdatei', 'r')
  oldcrc, newcrc = fritzchecksum.calc_crc32(myexport)

  ...

The module contains two Python 1st class citizens:

  - function *calc_crc32(fin, fout=None, logcb=log_null)*

    Calculates the CRC of a Fritz!Box configuration export file and writes
    the new CRC sum to a new configuration file

    Accepts:

      - fin: a file-like
      - fout: None or a file-like object. If a file, then the input will be
        written to the output with the new calculated CRC
      - logcb (default: ``log_null`` which is an empty stub)
        a logger which must a accepts \*args (print will work)

    Returns:

      (oldcrc, newcrc) -> tuple

      oldcrc and newcrc will be strings representing a CRC32 in hexadecimal
      format if everything went fine

      oldcrc can be ``None`` which means an ``IOError`` exception has been
      raised and the operation has not completed successfully. In that case
      the 2nd value in the tuple contains the raised exception

    Note: the escape character '\' is escaped iself in some of the
    lines. CRC calculation will be wrong if the character is not
    un-escaped.

    The file is composed of the following:

      - A global "CONFIGURATION EXPORT" section

        Some variables (a=b) may be defined at this level. This definition
        contributes to the the CRC calculation by concatenating a and b and
        null terminating the result.

      - Subsections:

        The name (null terminated) of the subsection contributes to the CRC
        calculation

        - XXXBINFILE Section

          Lines represent hexadecimal values. The values (binary converted)
          are used directly in the calculation of the CRC (stripping eol
          before)

        - CFGFILE Section

          It is a textfile embedded in the larger export file. All lines
          including '\n' contribute to the CRC except the last line which
          must be stripped of the EOL character before being included in
          the CRC calculation


  - class *ExportFile*

    Class to encapsulate the parsing of an export file and overwriting of
    the CRC value

    After loading a file it keeps the loaded content in an internal ``fout``

    With the following methods:

    - *load(self, fin, out=True)*

        Loads from a file-like/string object ``fin`` and will update internal
        ``status``, ``error``, ``oldcrc`` and ``newcrc``

        if ``out`` is ``False`` no internal buffering of the loaded input will
        be made

        Returns:
          tuple -> (status, error)

          If status is ST_OK (True) error will be None
          If status is ST_ERROR (False) error will be the raised exception

    - *load_file(self, fin, out=True)*
        Loads from a file-like object ``fin`` and will update internal
        ``status``, ``error``, ``oldcrc`` and ``newcrc``

        if ``out`` is ``False`` no internal buffering of the loaded input will
        be made

        Returns:
          tuple -> (status, error)

          If status is ST_OK (True) error will be None
          If status is ST_ERROR (False) error will be the raised exception

    - *save(self, fout)*
        Writes the internal ``self.fout`` file to a file-like/string ``fout``

        Returns:
          tuple -> (status, error)

          If status is ST_OK (True) error will be None
          If status is ST_ERROR (False) error will be the raised exception

    - *save_file(self, fout)*
        Writes the internal ``self.fout`` file to a file-like object ``fout``

        Returns:
          tuple -> (status, error)

          If status is ST_OK (True) error will be None
          If status is ST_ERROR (False) error will be the raised exception
