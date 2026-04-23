
# Goals

- Some review on newtons method
- When does a seed value attract to a given root?
- Some pretty images

## Newtons Method Review 
- What is newtons method?
- Visual explanation
- Show what happens at the boundry


## Introduction to Newtons Method
- Introduce Newton & John Method 
- Show the formula
- Talk about Newton's original use case & Raphson getting mogged
- Show iterative formula to recursive
- Geometric view
    - Some initial starting guess of x0
    - Apply function
    - Keep applying 
    - And with only 3 iterations its pretty good
    - Changing seed <=> viewing orbit
    - If a seed starts near a root it tends towards that root pretty consistently
    - The boundry between roots is where issues arise

## Newton Method Simpliciation
- A key simpliciation of the study of newtons method is focusing on *polynomials*, in our case we will focus our attention to cubics
- We can simplify further by talking about the polynomials in their factored form
    - The factored form is alot nicer as for smaller polynomials it cuts down on one variable
    - It also provides a symmetry in the equation where each root is interchangeable with one another
- As the focus of this paper / extension beyond what Newton used this method for - because of the fundamental thereom of algebra, you can always find roots for any given polynomial *as long as you allow the roots to take complex values*
- This means viewing our iterative function / map from a map between the real numbers to the real numbers as instead a map between the complex numbers to the complex numbers 
    - well technically most literature talks about map as one from the Rieman Sphere unto itself, also known as the extended complex numbers 
    - The key reason why this is done is that its simply a 'compact' set of the complex numbers adjoined with the point at infinity

## Newtons Fractal Intro/Complex Plane
