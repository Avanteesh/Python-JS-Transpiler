# Python to Javascript Source code Transpiler

<img src="/montages/Transpiler-Architecture.jpeg" height="500" />

So, I have been trying to explore really deep on Compilers, Linters and Programming languages in general, And this project was a fun one to build.
A transpiler takes existing source code's abstract syntax tree, and converts it into a target programming language. In this case I have made use of the 
Python's Abstract Syntax Tree and parse it down to Javascript source code, by using the lexial or grammar rules of Javascript language. An important point 
to be noted is If your transpiling python sources that have certain dependencies, it may not necessary transpile appropriate Target Javascript source. As shown 
in the picture, The orignal AST is converted into a Target AST, However in my case the approach is much simpler, we are just generating Javascript source code 
using the python's AST.

<b>Data Structure Singly Linked lists is utilized to check for Variable declarations and scoping</b>
<img src="/montages/lexical.webp" height="400" />

<h1>Tests</h1>
<img src="/montages/test-1.png" height="380" alt="test no. 1" />
<img src="/montages/test-2.png" height="380" alt="test no. 2" />
<img src="/montages/test-3.png" height="380" alt="test no. 3" />
<img src="/montages/test-4.png" height="380" alt="test no. 4" />
