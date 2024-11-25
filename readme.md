# ada-L - A Modern Tribute to Lovelace


![Logo](logo.png)


#   Language Documentation


## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Language Basics](#language-basics)
4. [Data Types](#data-types)
5. [Variables](#variables)
6. [Control Structures](#control-structures)
7. [Functions](#functions)
8. [Structures](#structures)
9. [Modules](#modules)
10. [Cheat Sheet](#cheat-sheet)

## Introduction
**! The ada-L project is still under development, and this is version 1.0 !**

ada-L is a simple, intuitive programming language designed for educational purposes. It combines familiar syntax with powerful features like structures and modules.

## Installation
```bash
# Clone the repository
git clone https://github.com/D4L1IR3Tr0/ADA_project.git

# Run an ada-L program
python3 interpreter.py program.ada

# To install VSCODE extension for ada-L
cd extentionVSCODE
chmod +x install.sh
./install.sh
```

## Language Basics

### Comments
```ada-L
-- Single line comment
-* Multi-line
   comment *-
```

### Basic Syntax
- Each statement ends implicitly at the end of line
- Code blocks are marked with `:` and `/.`
- Indentation is recommended but not required

## Data Types

### Basic Types
- `int`: Integer numbers
- `float`: Floating-point numbers
- `double`: Double precision numbers
- `string`: Text strings
- `bool`: Boolean values (true/false)
- `array`: Arrays of values

### Type Declaration
```ada-L
int x <- 5
string name <- "John"
bool isValid <- true
double price <- 3.14
```

### Arrays
```ada-L
int[] numbers <- [1, 2, 3, 4, 5]
int value <- numbers[0]  -- Access first element
```

## Variables

### Declaration and Assignment
```ada-L
-- Declaration with initialization
int age <- 25

-- Declaration only
int count
count <- 0

-- Multiple assignments
int x <- 1
int y <- 2
x <- y  -- x now equals 2
```

### Compound Assignments
```ada-L
x += 5   -- Same as: x <- x + 5
x -= 3   -- Same as: x <- x - 3
x *= 2   -- Same as: x <- x * 2
x /= 4   -- Same as: x <- x / 4
```

## Control Structures

### If Statement
```ada-L
if (condition):
    -- code
else:
    -- code
/.
```

### Loops

#### Range Loop
```ada-L
loop [0..5]:
    write("Hello")
/.
```

#### Iterator Loop
```ada-L
loop i in [0..5]:
    write(i)
/.
```

#### While Loop
```ada-L
loop (condition):
    -- code
/.
```

#### For Each Loop
```ada-L
loop item in array:
    write(item)
/.
```

## Functions

### Function Definition
```ada-L
define add(a, b):
    out(a + b)
/.

-- With default parameter
define greet(name <- "World"):
    out("Hello " + name)
/.
```

### Function Call
```ada-L
add(5, 3)
greet()
greet("John")
```

## Structures

### Structure Definition
```ada-L
make person:
    int age
    string name
/.
```

### Structure Usage
```ada-L
-- Create instance
person p <- person(25, "John")

-- Access members
write(p.name)
write(p.age)

-- Modify members
p.age <- 26
```

## Modules
- For now there are two premade modules : 
- **math.ada**
- **io.ada**
### Module Creation (math.ada)
```ada-L
-- math.ada
define square(x):
    out(x * x)
/.

define cube(x):
    out(x * x * x)
/.
```

### Module Import and Usage
```ada-L
@import <math.ada> as math

write(math.square(4))  -- Outputs: 16
write(math.cube(3))    -- Outputs: 27
```

## Cheat Sheet

### Basic Syntax
```ada-L
-- Variables
int x <- 5
string name <- "John"
bool flag <- true

-- Arithmetic
x + y    -- Addition
x - y    -- Subtraction
x * y    -- Multiplication
x / y    -- Division
x % y    -- Modulo

-- Comparison
x == y   -- Equal
x != y   -- Not equal
x < y    -- Less than
x <= y   -- Less or equal
x > y    -- Greater than
x >= y   -- Greater or equal

-- Logical
&& -- AND
|| -- OR
!  -- NOT

-- Input/Output
write("Hello")
value <- read("Enter value: ")

-- Control Structures
if (condition):
    -- code
else:
    -- code
/.

loop [0..5]:       -- Range loop
loop i in [0..5]:  -- Iterator loop
loop (condition):  -- While loop
loop item in arr:  -- For each loop

-- Functions
define functionName(param1, param2):
    out(param1 + param2)
/.

-- Structures
make structName:
    int field1
    string field2
/.

-- Modules
@import <module.ada> as mod
```

### Common Functions
```ada-L
-- Mathematical
math.pow(base, exp)    -- Power
math.sqrt(x)           -- Square root
math.abs(x)            -- Absolute value
math.min(x, y)         -- Minimum
math.max(x, y)         -- Maximum

-- Conversion
int <- convert(string, "int")     -- String to int
string <- convert(int, "string")  -- Int to string

-- Input/Output
write(value)                      -- Display value
value <- read("Enter value: ")    -- Read input
```

### Best Practices
1. Use meaningful variable and function names
2. Comment your code for clarity
3. Indent your code for readability
4. Break down complex problems into functions
5. Use structures to organize related data
6. Import modules to reuse code
7. Handle errors appropriately
8. Test your code thoroughly

### Common Pitfalls
1. Forgetting to end blocks with `/.`
2. Using undefined variables
3. Wrong data type conversions
4. Incorrect operator precedence
5. Missing function parameters
6. Incorrect structure member access
7. Module import path errors

### Debug Tips
1. Use `write()` to debug values
2. Break down complex expressions
3. Check variable types
4. Verify module imports
5. Test functions individually
6. Use meaningful error messages

This documentation provides a comprehensive guide to the ada-L language. For more specific use cases or advanced features, please refer to the individual sections or contact me.

