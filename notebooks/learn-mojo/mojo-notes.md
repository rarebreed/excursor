# Mojo notes

These notes will be in md format until the mojo SDK is released in September.

This document is currently written for readers who already have experience with a programming language, so it will not
start from first principles.  There will be frequent references to rust, but it is not required to know rust.

There will also be frequent comparisons to python, since mojo aims to be a superset of python.  Therefore, ideally, you
should know python as well.  However, this is also not strictly necessary, and overtime, I will write the document to
teach both python and mojo basics as mojo gains more compatibility with python.

## Some limitations to note in mojo

While mojo aims to be a superset of python, it is not yet there.  Some current limitations are the following:

- No top-level variables (ie, variables that don't live inside a function or struct)
- No python `class` type (but it does have `struct` which is the non-dynamic version of a class)
- The SDK to run locally is only available on x86_64 for linux (ubuntu)
- `def` is not fully equivalent to python's def yet (eg, mojo's scope is different)
- See [proposal on dynamism](https://github.com/modularml/mojo/blob/main/proposals/mojo-and-dynamism.md) for more details on mojo's lack of dynamism

## Functions in Mojo

The bread and butter of almost all languages (java being a lonely outlier) are functions, and mojo is no exception.  In mojo,
there are two ways to define a function:

- like python with `def`
- or with `fn`

> **Parameter vs Argument**
> 
> Many languages treat parameters and arguments as synonyms, but mojo has a more precise definition.  A parameter is what is in
> the declaration of the function and is therefore compile time.  An argument is the runtime type/value that gets passed into
> the function when it is called, and is therefore known at runtime.  This dovetails nicely with mojo's Parameterized Expressions
> which are like generics and functions that can run at compile time.

If using a `def` definition, type annotations for are not required (though still recommended) for a function's parameters or in the
body of the function.  If using a `fn` definition, then the type annotations are required both for parameters, and for any locally
declared variables in the body.

Mojo uses a slightly modified version of the PEP-695 syntax (forthcoming in python 3.12 due out in early October 2023).  Unlike
python type annotations where the return type can be inferred, in mojo, you must still specify the return type if using `fn` 
definition.

> **Async**: Mojo also has support for `async fn` and `async def` as well, along with the `await` keyword.

Here is an example of a simple mojo function

```python
fn my_relu(x: Int, y: Int = 10) -> Int:
    let result: Int
    if x >= y:
        result = x * 2
    else:
        result = x
    return result
```

### Declaring (Im)Mutability: let and var

In mojo fn's or struct fields, you must declare local variables either with `let` or `var`.

- `let` is for immutable variables
- `var` is for mutable variables

In rust, `let` and `let mut` would be the equivalent identifiers.

> **Mojo Update**
> According to the mojo proposals for keyword renaming, the `let` may be renamed, and `var` might serve double duty

## Argument passing

Some programmers may not even understand what _argument passing_ means.  Some languages have only one way to do it, like
python.  Or it may have something awkward like java (which differentiates between Objects and primitives) and do
Boxing and Unboxing when the arguments are primitives, thereby causing a performance hit.  And since (Un)Boxing is 
implicit, it is not obvious that there are different ways to pass args to java methods.

So if you are not familiar with the terms, there are generally two different kinds of argument passing:

- by value: (sometimes called by-copy) where the value of a variable is used
- by reference: where the value is indirectly retrieved through reference or pointer dereferencing

This is sometimes confusing to people, because pointers or references can be hard to conceptualize.  If it helps, think
about _value equality_ versus _identity equality_ which is what Java does.  By default, in java, the `==` operator
compares _identity equality_, meaning "does this variable point to the same memory as this other variable?".  But 95% of
the time what we care about is _value equality_, or "does this variable have the same contents of this other variable?".

Also, a brief discussion of `ownership` needs to be mentioned.  Similarly to rust, mojo has a concept of ownership which
basically just means "who is responsible for cleaning up this data?".  In languages without Garbage Collectors, this is
very important (and is what C and C++ lack).

In mojo, by default, all parameters are immutable and passed by reference (an implicit keyword `borrowed` is added as a 
prefix to the parameter name so that `foo(borrowed age: Int)` and `foo(age: Int)` are equivalent). However, there are 
several ways to pass arguments to functions in mojo. An argument to a function can be:

- **moved**: (aka _transferred_) where the ownership and _value_ of the argument is transferred to the function
    - The type of the parameter must have a `__moveinit__` method defined
    - In the fn declaration, the parameter name will be prefixed with `owned` keyword
    - On the caller side, the argument is postfixed with the `^` symbol (eg `foo(age^)`)
    - Once moved, the original variable is no longer accessible (technically, it could be zeroed out but cant be reached)
    - _moves_ also happen in assignment, when the RHS variable is post-fixed with the `^` sigil (`let obj2 = obj1^`)
- **by reference (immutably)**: where a shared reference to the argument object is passed in 
    - This is the default, and an implicit `borrowed` keyword is prefixed before the parameter name
    - No mutation of the argument can occur
    - the compiler will keep track that the argument object has been borrowed immutably
    - Since the reference is obtained immutably, there can be many other immutable borrows
        - ie, the argument could be passed immutably to another fn
- **by reference (mutably)**: where an exclusive mutable reference to the argument object is passed in
    - The fn declaration parameter name is prefixed with `inout`  (eg `foo(inout age: Int)`)
    - Since the argument value passed in can be directly mutated, it is **not** a copy of the data
    - Since it is a mutable reference, only one such mutable (aka exclusive) reference can exist in the lifetime of the
      use of the function

> **Mojo Update**
> >
> There is some discussion on whether to rename some keywords. Notably `borrowed` may become `ref` and `inout` might
> become `refmut`.  This is due to some changes they may need to make for `lifetimes`.  Also, they will probably change
> they keywords to _modify the type_ rather than modify the parameter _name_.  For example:
> ```python
> # Current way
> fm modify_employee(inout employee: Employee): ...
> # Proposed way
> fn modify_employee(employee: refmut Employee): ...
> ```

Note that the default behavior is opposite to rust.  In rust, the default is to pass by value and to _move_ it (the data
is transferred and then once out of scope is gone).  Mojo takes the stand that it is more common to want to pass by
(immutable) reference and makes this the default.  This is also more similar to how python works, although most things
in python are a mutable pass by reference (eg, lists, dicts, and most classes). You therefore do not need to mark the
argument with a sigil (like `&foo`) that rust requires when you _do_ want to pass by immutable reference (they did
however consider this, and may reintroduce it depending on how their lifetime system works).

When you do want to pass by value and _move_ it, then you do this in mojo

```python
# For the following code to work, MyStruct must implement __moveinit__

fn foo(owned data: MyStruct):
    # do something with data
    ...

let obj = MyStruct()
foo(obj^)  # think of the ^ like it's being given up
print(obj) # will fail, because obj was moved

# Or in assignment
let obj2 = MyStruct()
# after this, obj2 is no longer accessible.  
# Without the ^, it would be a _copy_ and not a _move_ (and MyStruct would have to implement __copyinit__)
let obj3 = obj2^  
```

When you want to pass by _mutable_ reference in mojo, you would use the `inout` keyword modifer to a parameter

```python
def foo_by_mut_ref(inout data: MyStruct):
    data.value = 10

obj = MyStruct()
foo_by_mut_ref(obj)  # obj still exists and was mutated
```

## Copy vs Move vs Reference

Unlike rust, mojo allows you to make types moveable or not (in rust, the affine type system requires all types to
transfer the data and then effectively delete the old value, placing a lot of stress on memcpy performance).  In rust,
one usually adds the `Copy` and/or `Clone` auto derived traits to a type to make it copy-able (shallow or value-wise) 
or cloneable (deep...for copying ref data).

In mojo, copying is done manually by implementing a `__copyinit__` dunder method.  It is optional, but without an
implementation, you can not put the type on the right hand side of an assignment.  Eg

```python
# A type without a copy or move constructor
struct Foo:
    let age: Int

    def __init__(inout self, age: Int):
        self.age = age

obj = Foo(10)
let obj2 = obj  # will fail here, because this would be a copy and there is no __copyinit__ implememted
```

> **Note**: I will use the acronym RHS for right hand side, and LHS for left hand side 

After an assignment where the RHS type implements `__copyinit__`, the variable on the RHS is still available.  This is
like a rust type that implements the `Copy` trait.  If a rust type does not implement the `Copy` trait, then the 
variable RHS would have been _moved_ into the variable on the LHS.

I try to analogize that `__copyinit__` and `__moveinit__` are like the unix `cp` and `mv` commands respectively.
With the `cp` command, the original source file will still exist after being called, whereas in the `mv` command,
the source file will no longer exist.

> **Food for thought**
>
> In rust, you don't have a choice whether a move will happen or not.  What about mojo? So this begs a couple of
> questions:
>
> - What happens if you have neither a `__copyinit__` or `__moveinit__` defined?
> - Why wouldn't you want a `__moveinit__` (or `__copyinit__`) defined?
> - What exactly is moved?

To answer the questions above, we need to consider what a variable _really_ is.  We will cover this in a later section.

In a move, the value stored at the memory location of the RHS is copied over to the LHS, and then the memory for the RHS
is deleted. In rust's case, the drop doesn't actually happen until the end of the scope, whereas in mojo it's as soon as 
the variable is no longer used anymore...even within the same scope.  This has a couple of advantages for mojo compared 
to rust by eliminating the need for [dynamic drop flags](https://doc.rust-lang.org/nomicon/drop-flags.html).

But what about references?  Currently, mojo doesn't have explicit references.  They do have `ref` and `mut ref` as
reserved keywords, but they are still working on fleshing out their lifetime system.  That being said, whenever you pass
a variable into a function, by default, it's being passed in as an immutable reference (the data is neither being copied
nor moved into the function).  Unless a parameter is marked with `inout`, so that it is a mutable reference, or with the
`owned` prefix, so that the variable itself is moved, the argument is passed in by immutable reference.

> **But Why?**
>
> The reason mojo choose this as the default, is that they believe this is the more common scenario, and it (somewhat)
> dovetails with how pythonistas program.  Since everything is an object (lives on the heap) in python, everything in 
> python is passed by reference.  Whether it is a mutable or immutable reference depends on the type in python.

In rust, it defaults to move semantics, and therefore pass by value.

### Why does it matter?

First off ask yourself

- Why do we even need to make the distinction between copy and move?  
- Wouldn't it just be easier to always copy data?
- Or conversely, always directly update the value itself through a mutable reference instead of a copy (as python does)?
- And why a move if we can just copy? What good does transferring data do?

Some of the answers to those questions requires an understanding of memory, and the performance characteristics of
accessing the values stored in memory.  If copies were cheap, then it probably would make sense to always make a copy,
unless your goal was to make the change visible somewhere else (ie, in another thread). But copying is not always cheap.

> Dynamism's performance cost
>
> Part of the reason python is slow is because in python everything is an `object` (somewhat equivalent to Java's Object)
> and requires:
> - A memory access to get the object's memory location (which is a glorified hash table)
> - Retrieval of the value of the key, which is another memory retrieval that may not reside in cache
> While mojo can go to heroic lengths for parallelism (eg SIMD data types that make use of CPU's vectorized registers),
> one of the more mundane performance improvements is simply by removing dynamism and specifying types.  For example,
> In python, a class can have methods and fields dynamically added, removed, or changed at runtime.  The _raison d'etre_
> of mojo `fn` and `struct` as equivalents of python's `def` and `class` is to remove this dynamism.

What about _moves_?  Rust makes it central to the language, because its affine type system requires it.  So it must be
better than copying right?  Moving data has benefits to compiler analysis, because it means the other variable no longer
exists.  The affine type system guarantees that a variable is used _at most once_ (related to _linear type system_ which
guarantees that a type will be used _exactly once_).  In order to be used more than once (used, meaning passed to a
function, or assignments), requires a reference to the variable, and not the variable itself.

However, moves, like copy, will (usually) require transfer of data from one memory location to another and will always
require (at some point) calling the memory destructor to free up the memory of the old now moved data. For stack
allocated data, memory clean up is cheap (basically, just moving the register base and stack pointers) (TODO: verify
this is still true, as new security features in processors may now zero out memory on the stack so that the old
data can't be read either as a bug or an exploit which can happen if the processor just overwrites the stack frame
by shifting the stack and base registers to point to the next stack frame), but not for heap allocated data. Any time 
data is transferred, it triggers a cascade of operating system syscalls and hardware events that cost time.

So let's dive in, and consider what a variable really is under the hood.

### A variable's multiple identities

All of the above is to show that memory is a severe bottleneck to performance, and it's a reason why it's good to know
why there are copies, moves, and references in the first place.

This is not specific to mojo, but is required understanding nevertheless.  This knowledge will help in understanding how
and why copy and move constructors may or may not be needed in low-level system's programming languages such as mojo, 
rust, or C++.

Typically, in high level languages, when we think of a variable, we only think about the data that it represents.  The
variable **is** the data is how we tend to think of it.  But sometimes, this way of thinking gets us in trouble.  A 
variable is really: a name, which points to some memory, and that memory holds some value(s).

So, let's break up that statement into its discrete parts:

- `a name`:  this is the symbol that is used to (ultimately) give access to data depending on the scope
    - The name must first be looked up, because there may be the same name in different scopes
    - In python there are 4 different kinds of scopes (soon to be 5 in 3.12)
    - The namespace is like a dictionary that maps the symbol name, to the object (really, its memory)
    - Python has some rules about how to look up the name in the nested namespaces (so mojo should too)
- `which points to some memory`: there are actually several regions of memory
    - **registers**: which are in the CPU itself
    - **cache**: multiple levels of cache with different latency access
        - cache line: the minimum amount of memory that can be read from or written to the cache
        - cache tag: a subset of the _physical memory_ address used as a lookup (including index, offset, and set)
        - write policy: the policy of when to write data back to memory in a cache miss (see cache coherency)
        - cache coherency: a problem that occurs when cache and 
    - **stack**: a region in memory (typically high address range depending on OS and CPU arch)
        - Since the stack is frequently accessed, it is often in the cache
        - Due to the way cache lines work, when memory is contiguous, it will also pull in "nearby" data into the cache
            - Therefore, variables in the same stack frame often get pulled into the cache as well
        - The stack grows down (when it starts at a high address)
    - **heap**: a region in memory (typically low address range)
        - One reason arrays are faster than maps/dicts is because the data is contiguous.  
        - This has the benefit that data nearby data is pulled into cache
        - With maps or most data structures with pointers, the pointers to fields/values may be "far away"
        - The heap (usually) grows up when it starts in the low address (but actually, the memory allocator
          will scan the free blocks to find a block of memory of a size that fits the request)
            - This is why memory fragmentation is a thing, and can affect rust (and mojo too, since it has no GC)
    - understanding performance with memory is difficult, because it requires some understanding of:
        - physical vs virtual memory (and cache -> cache lookup -> TLB lookup -> memory or paging)
        - TLB: Translation Lookaside Buffer, which is a hardware cache of virtual -> physical addressing
        - Page Tables: a Page is a data structure the OS uses to know what has been mapped to physical memory
            - and contains a _dirty_ bit (a block has been modified and saving to disk, and cache needs updating)
        - Cache miss: when the CPU has to fetch data from main memory (and written to cache depending on strategy)
        - TLB miss: is when data isn't in the memory and has to be fetched from disk (ie, paging, aka swapping, occurs)
- `that memory holds some value`: the term value is tricky, because the value stored in memory may also be a reference
    - in python, _everything_ is a an object, including things like int and float
    - Memory has an address and it is the starting location for how the interpreter (or compiler in mojo's case)
      interprets the value stored at that address (the value meaning the raw bits)
        - This is why in system languages like rust and mojo, we must know the _size_ of the data type
        - Given the size of a data type, and its starting memory address, we can interpret the bits into a type
    - there is no pass by value in python, however there are immutable data types like int or str that seem that way
    - This is why when you pass most objects in python to a function, any modification is seen after the function
        - With immutable data types, like int, str, or tuple, a _new_ object
    - in mojo, the memory storing a variable's value might be:
        - the actual data on the stack
        - a pointer referencing another address in memory (whose value could hold another indirection recursively)
        - a register value (it actually gets passed directly to a register rather than the stack)

So as we can see, it's more complicated in mojo.  But that's how mojo and other system languages are faster, because
they don't always have to reach out to memory (a reference) to retrieve the actual value.  In mojo's case, unlike rust,
it actually has the power to directly store a variable into a register through the @register_passable decorator (in rust
, you would need to inline assembly to do that). This means that some familiarity with the stack and the heap are 
somewhat required (even moreso than rust, because currently, in order to create a list or vector data type in mojo, you
currently need to roll your own through pointer semantics).

### The Copy Constructor: __copyinit__

Technically, mojo doesn't use the terms copy constructor or move constructor (like C++ does), but it may be helpful to
think of `__copyinit__` as constructing a "new" value.  I put "new" in quotes, because the implementation of
`__copyinit__` (that you yourself define in your own structs) might simply increment a ref count and make the 
new value a reference to an existing value (which is much more performant than allocating a block of memory the size
of the RHS type, and inserting copies of values into the new memory).  Or, the implementation could do a value-wise
deep copy from the RHS object to the LHS

> Rust Copy vs Clone
>
> If you are familiar with rust, rust makes a distinction between Copy and Clone (where Clone is a subtype of Copy)
> In rust, a Copy type is meant for data types that are mainly direct values and don't have any references inside
> the data type.  This makes them cheap to create new values.  A Clone type is meant for data types that have
> references, ie, data that lives in the heap.  Creating a clone is therefore more expensive.  Part of the rationale
> for the difference is that rust _must_ be able to _move_ values in function passing or assignment, and a type
> implementing the Copy trait determines whether the RHS still exists or after assignment or passed to a function
> not as a reference (eg `foo(&some_var)`)
>
> Mojo does not make this distinction with the `__copyinit__` method.  You can choose to do something like Rust's
> Copy or Clone, though rust's distinction is useful.

Let's think about vanilla python and look at this code

```python
data = {
    "x": 10,
    "y": -3
}

new_data = data
data["x"] = 20  # stop for a second and ask yourself, do i need _data_ anymore?

# what will this print?
new_data["x"]
```

In the rust language, after `new_data` was assigned the value of data, data is no longer accessible.  It's _value_ was
moved (effectively the name lookup of `data` is no longer bound).  In python, as you can see, the `data` variable is
still alive and well.  But if you think about it, why do we need to keep `data` around?  After all, didn't I just copy
over its values to `new_data`?

Actually no, the _value_ of `data` was not copied over.  Python just made `new_data` map to the same address that 
`data` was pointing to, and incremented the ref count.  Any changes to `data` happen in `new_data` and vice-versa.
Sometimes, this is what you want.  But sometimes, you want a brand new copy of the _value_.  This way I can make changes
to `new_data` without it changing `data` also.

In python you would do this:

```python
data = {
    "x": 10,
    "y": -3
}
new_data = data.copy() # works because we have shallow data (the values are not nested references)
new_data = dict(data)  # same, we have shallow data
new_data = {k:v for k, v in data.items()}  # verbose, and only for transforming
```
