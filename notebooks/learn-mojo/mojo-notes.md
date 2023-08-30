# Mojo notes

These notes will be in md format until the mojo SDK is released in September

## Mutability: let and var

In mojo fn's, you must declare local variables either with `let` or `var`.

- `let` is for immutable variables
- `var` is for mutable variables

In rust, `let` and `let mut` would be the equivalent identifiers.

## Argument passing

By default, all parameters are immutable and passed by reference (an implicit keyword `borrowed` is added as a prefix).
However, there are several ways to pass arguments to functions in mojo. An argument to a function can be:

- **moved**: where the ownership and _value_ of the variable is transferred to the function
    - The parameter type must have a `__moveinit__` method defined
    - In the fn declaration, the parameter name will be prefixed with `owned` keyword
    - On the caller side, the argument is postfixed with the `^` symbol (eg `foo(age^)`)
    - Once moved, the original variable is no longer accessible (technically, it could be zeroed out but cant be reached)
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

Note that this is opposite to rust.  In rust, the default is to pass by value and to _move_ it (the data is transferred
and then once out of scope is gone).  Mojo takes the stand that it is more common to want to pass by (immutable)
reference and makes this the default.  This is also more similar to how python works, although most things in python are
a mutable pass by reference (eg, lists, dicts, and most classes). You therefore do not need to mark the argument with a
sigil (like `&foo`) that rust requires when you _do_ want to pass by immutable reference (they did however consider
this, and may reintroduce it depending on how their lifetime system works).

When you do want to pass by value and _move_ it, then you do this in mojo

```
fn foo(owned data: MyStruct):
    ...
    # do something with data

let obj = MyStruct()
foo(obj^)  # think of the ^ like it's being given up

# Or not in a function but in assignment
let obj2 = MyStruct()
let obj3 = obj2^  # after this, obj2 is no longer accessible.  Without the ^, it would be a _copy_ and not a _move_
```

When you want to pass by _mutable_ reference in mojo, you would use the `inout` keyword modifer to a parameter

```
def foo_by_mut_ref(inout data: MyStruct) -> MyStruct:
    data.value = 10
    return data

obj = MyStruct()
let new_obj = foo_by_mut_ref(obj)  # obj still exists and was mutated
# For this assignment to work, MyStruct must implement __copyinit__
```

## Copy vs Move

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

After an assignment, the variable on the right hand side (RHS) is still available.  This is like a rust type that 
implements the `Copy` trait.  If a rust type does not implement the `Copy` trait, then the variable RHS would have been
_moved_ into the variable on the left hand side (LHS).  But what exactly is moved?

### A variable's multiple identities

This is not specific mojo, but is required understanding nevertheless.  This knowledge will help in understanding how
and why copy and move constructors may or may not be needed.

Typically, in high level languages, when we think of a variable, we only think about the data that it represents.  The
variable **is** the data is how we tend to think of it.  But sometimes, this way of thinking gets us in trouble.  A 
variable is really: a name, which points to some memory, and that memory holds some value(s).

So, let's break up that statement into its discrete parts:

- `a name`:  this is the symbol that is used to (ultimately) give access to data
- `which points to some memory`: most languages actually have some kind of mapping of the name to a memory location
    - these are usually called namespaces, and namespaces are often created at each scoping level
    - in python, there are several scopes, the one tripping people up the most being the function scope
    - there are actually several regions of memory
        - registers: which are in the CPU itself
        - cache: with different levels, if 
- `that memory holds some value`: the term value is tricky, because the value stored in memory may also be a reference
    - in python, _everything_ is a reference to data, not the data itself
        - there is no pass by value, however there are immutable data types like int or str that seem that way
    - in mojo, the memory storing a variable's value might be:
        - the actual data on the stack
        - a pointer referencing another address in memory (whose value could hold another indirection recursively)
        - a register value (it actually gets passed directly to a register rather than the stack)

So as we can see, it's more complicated in mojo.  But that's how mojo and other system languages are faster, because
they don't always have to reach out to memory (a reference) to retrieve the actual value.  This means that some
familiarity with the stack and the heap are somewhat required (even moreso than rust, because currently, in order to
create a list or vector data type in mojo, you currently need to roll your own through pointer semantics).

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

Actually no, the _value_ of `data` was not copied over.  Python just created a new pointer to the same address that 
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
