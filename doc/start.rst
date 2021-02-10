start
======


Getting started: What chefkoch does upon invokation
####################################################

1. **Load the Configuration**
    1. Create an empty Configuration object, this object already contains the default values for all configuration options that have default values (i.e. {'cheffile': './cheffile'})
    2. Parse the fixed command line arguments for the cheffile definition (i.e. '--cheffile')
    3. Extend the configuration object by the contents of the cheffile
    4. Parse thefixed command line arguments for the "other" file definitions (those that can be defined as links within the cheffile), (i.e. 'kitchenfile', 'flavourfile', ...)
    5. Extend the configuration object by the contents of any linked file in the first level of the configuration
    6. Parse any other fixed command line arguments (those that have single-dash or double-dashes upfront their argument name)
    7. Parse any other command line arguments (additional options)

*Now, chefkoch knows all settings explicitly from the in-memory Configuraition objects. There are no links to any configuration files whatsoever that might impact what chefkoch does from now on (except throwing exceptions if something is inconsistent). Chefkoch is now in the "spoiled-child"-operation mode.*


2. **Populate the Fridge**
    1. Create a Fridge object
    2. For every resource entry in Configuration.resources, create an ItemShelf and create a Resource object for each file in the resource definition
    3. For every Flavour entry in Configuration.flavours, evaluate the explicit list of parameter variations from the configuration entries and create a FlavourShelf with this explicit list
    4. For every Recipe entry (these represent steps!) in Configuration.recipe, create an ItemShelf and create a Resource object for each of the step source definition files
       Example: (see above) `Configuration.recipe.compute_A.resource` points to the source code for this recipe. This file will be processed just as a regular resource (code file will be hashed and added to the ItemShelf for this resource accordingly)

*Now the Fridge contains Shelves for all resources and flavours and the entries in those shelves completely define the scope of flavours permutations (we'll need that later on). To be explicit: Every flavour is fully defined from the permutation of the FridgeShelf entries contained herein.*


3. **Create the Recipe object**
    1. Create a Recipe object based on the COnfiguration object and the freshly populated Fridge object. During the Instantiation of the Recipe object, the elements of the `Configuration.recipe` section will be iterated multiple times:
    2. Create a list of all result names (i.e. the outputs of each step). Throw an exception if any one of those step result names is already present in the Fridge as a FridgeShelf (that means that there would be wither a resource, step or parameter of exactly this name). Create an empty (we'll populate it later) ItemShelf for each of those names, just to catch if there are multiple output definitions (results)
    3. Scan all input names in `Configuration.recipe` entries. Throw an exception if for any name NO Shelf in the Fridge exists
    4. Scan the definition of the Recipe for circles (a circle occurs if an output is also input to itself or one if its prerequisite results)


**Intermezzo: Descriptio del situazzione**

Now we have the following situation: For all the objects in a chefkoch run, everyone of them has a unique name, there exists a Shelf in the Fridge. Depending on the type of resource these cases may occur:

  **A:**  The elements contained in a shelf are **resources**. Then the FridgeShelf itself is an instance of `ItemShelf` and contains at least one element (the resource or variations of it). Variations might occur if multiple resources are defined, i.e. when there are multiple source files defined for a step
  
  **B:**  The elements contained in a shelf are **parameters**. Now, the FridgeShelf itself is an instance of `FlavourShelf` and contains a list holding the variations of this parameter in clear type (no generators planned yet). Here, also multipe entries will lead to a variation. An empty `FlavourShelf` shall raise a Warning and later in the code (when we actually need this), should then raise an Error. The distinction is neccessary to allow the user (when partially cooking a recipe) to still have some unpopulated parts while being able to debug the way through the work-in-progess.

  **C:**  The elements contained in a shelf ar **results**. Here we require the FridgeShelf to be an instance of `ItemShelf`, but this time it has to be empty, since we do not have any results yet or even know which results there might be.

    For implementation ease, `FridgeShelf` should be able to
    - report the number of elements contained via `shelf.__len__` (resulting in `len(shelf)` being valid code)
    - iterate the number of elements contained via `shelf.__next__` and `shelf.__iter__` (enabling `[for bla in shelf]`)


4. **Create a Plan**

To form a plan we need to know which elements to produce (cook) during the chefkoch run (and lots of welding).


 1. Initialize an empty set `required`, that collects which Shelves must be considered to produce the set of given targets. 
 
 2. This set is populated by iterating all targets in the following scheme:
    *To avoid doing too much unneccessary stuff, keep a "visited" list of elements-of-interest during the following recursion that can shortcut already processed parts of the graph: Whenever a result was processed (and therefore further recursion was applied), we add it to this visited set and flag it as "processed" in case we come along this result at some other point of the recipe again)*
     
     **a.**  Consider the target to be the first element-of-interest 
        in (b. and c.) and start the following recursion:
    
     **b.**  If the element of interest is a resource or a parameter,
        add the name of the parameter or target to `required` 
        (the easy case) and stop this recursion chain.

     **c.**  If the element of interest is a result (an outbound edge 
        of a recipe entry), then we find the step in the recipe
        that produces this result and add this to `required`, 
        repeating (c.) for all of its connected input edges (the 
        Fridge-names mapped to step's input list). If any of these 
        edges fulfil (b.), stop this recursion chain accordingly
    
 3. Create a `remaining` set as a copy of `required`, from which we cross-out already processed elements. Also create an empty list `jobs` that collects the created `ResultItem` objects in the order of creation.

 4. Now, since we know that parameters and resources are non-empty Shelves, while results are empty Shelves, we iterate the `remaining` list as follows:

    **a.**  For an element in `remaining`, check if the FridgeShelf corresponding to the name of the element is not empty.
    
    **b.**  Create a `variants` list with one element: An empty `JSONContainer` object, that will hold the references to all dependencies of this step. As an outlook, after the following steps we will end up with a list of `JSONContainer` objects in `variants`, where each entry holds one of the encountered variations of this step.


      **b1.**  First of all, we add the reference to the step's source resource object to the `JSONContainer` object.

      **b2.**  Now we iterate all input connections to the step that point to another `ResultItem`. \
      Each of the input connections points to the `ItemShelf` in the Fridge, that holds all applicable variations of that result. 
      We will permute our already existing list of `variants` with the list of variations of that particular connection. \
      For every variation in the referenced `ItemShelf`, we add the named reference into the particular permuted `JSONContainer` object (e.g. `stepname.inputname=variantname`) and also merge its JSONContainer into the resulting `JSONContainer`. \
      This way we fully keep track of all dependencies that one particular variant encountered. During merging we need to be careful that we exclude conflicting dependencies (i.e. when one of the variant's dependencies was already defined by some other variation along the path: then we must exclude this conflicting configuration). \
      After this step we end up with a full permutation of all possible variants (of `JSONContainer`) of this particular result, based on all previous results this step depends on, while also keeping a conflict-free track record of all dependencies along the track.

      **b3.**  Finally, we add any Resources and Parameters that are defined as inputs to this particular result, but are not yet present in the `JSONContainer`. That indicates that none of the `ResultItem`-based dependencies so far along the way has required one of these Resources or Parameters and therefore no particular variant of them were chosen. That leaves us with having to permute all of the variants of that particular Parameter or Resource.

    **c.**  For every item in the `variants` list we now create a `ResultItem` object with the `stepName` and the `JSONContainer` as present in the `variants` item. \
    During the instantiation of `ResultItem`, the instance will be added to the `ItemShelf` of the name `stepName`. \
    (This should ideally be a method of `FridgeShelf`, which should distinguish between `ResourceItem` and `resultItem`, since these generate their `ItemShelf`-hashes differently) \
    Hashing of the `JSONContainer` and storing of its contents takes place now, when this particular element is acquainted with the `ItemShelf`, since only the shelf itself may detect or resolve hash collissions. For `ResultItem.JSONContainer` objects, hash collissions may be resolved easily through a full file comparision in case of matching hashes, since these meta records are fairly small in size. For `ResourceItem` objects however, there probably should be some configuration switches in place that control how chefkoch handles these cases. (It could become quite cumbersome if that 2TB resource file needs to be re-hashed fully for every variation of every step)

    **d.**  Add the just created `ResultItem` object to the `jobs` list.

    **e.**  Remove the just processed entry from the `remaining` list.
 
 5. If the number of elements in the `remaining` list reaches zero, the `jobs` list is complete and contains the list of results, that need to be processed, in the correct order. This is the plan that we now pass on to the scheduler in the next step. If the list of elements in `remaining` does not change over one full iteration of (4.), then there is a missing dependency and an error shall be produced.


5. **Instantiate the Scheduler and execute the Plan**

    *I love it when a plan comes together -- Hannibal Smith (The A-Team)*
    
    1. Walk through the `jobs` list and update the status of all `ResultItem` therein (meaning: check if it already was processed successfully already)
    2. All remaining elements must be issues for processing: *tbd*