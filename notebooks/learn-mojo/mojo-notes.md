# Mojo notes

These notes will be in md format until the mojo SDK is released in September

## Mutability: let and var

In mojo fn's, you must declare local variables either with `let` or `var`.

- `let` is for immutable variables
- `var` is for mutable variables

In rust, `let` and `let mut` would be the equivalent identifiers.

> **Mojo Update**
> According to the mojo proposals for keyword renaming, the `let` may be renamed, and `var` might serve double duty

## Argument passing

Some programmers may not even understand what _argument passing_ means.  Some languages have only one way to do it, like
python.  Or it may have something awkward like java (which differentiates between Objects and primitives) which will do
Boxing and Unboxing causing a performance hit, and makes it not obvious that there are different ways to pass args to
functions.

So if you are not familiar with the terms, there are generally two different kinds of argument passing:

- by value: where the value of a variable is used
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

- **moved**: where the ownership and _value_ of the argument is transferred to the function
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
> There is some discussion on whether to rename some keywords. Notably `borrowed` may become `ref` and `inout` might
> become `refmut`.  This is due to some changes they may need to make for `lifetimes`.  Also, they will probably change
> they keywords to _modify the type_ rather than modify the parameter _name_.  For example:
> ```
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

```
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

```
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

```
# A type without a copy or move constructor
struct Foo:
    age: Int

    def __init__(inout self, age: Int):
        self.age = age

obj = Foo(10)
let obj2 = obj  # will fail here, because this would be a copy and there is no __copyinit__ implememted
```

> **Note**: I will use the acronym RHS for right hand side, and LHS for left hand side 

After an assignment, the variable on the RHS is still available.  This is like a rust type that implements the `Copy`
trait.  If a rust type does not implement the `Copy` trait, then the variable RHS would have been _moved_ into the
variable on the LHS.  

> **Food for thought**
>
> In rust, you don't have a choice whether a move will happen or not.  So this begs a couple of questions:
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

### The Copy Constructor

The copy constructor is needed when you want to copy the _value_ of a variable on the RHS of the `=` sign, to a new
variable on the LHS.

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
