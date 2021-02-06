..  Copyright 2019 Christoph Wagner
        https://www.tu-ilmenau.de/it-ems/

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

.. _architecture:

Architecture OLD
================


The architecture is described from two points of view.
The first explanation is given with regards to the functionality of the system.
The second explanation describes the structure of the software architecture divided into frontend, backend and database.

Chefkoch is a tool to manage the computing process of simulations that are often repeated with only small changes in input or parameter data.
Starting the simulations and collecting the results manually is a big threat to consistence as it is easy to falsely use wrong parameters or old intermediate results.
Also, it is hard to decide which parts of the simulation need to be repeated and which parts are not affected by a change to only a few parameters.
There is the potencial to save computing time.

The project name Chefkoch which means chef cook evolved from the following conceptual idea.
Chefkoch is the head of the simulation computing process and coordinates different parallel threads as a chef coordinates kitchen assistants.

.. tikz::

    \tikzstyle{every node}=[line width=0.75pt]

    % Assistant Layers
    \draw    ( 2.4,0.40) -- ( 2.4,5.60) ;
    \draw    ( 2.4,0.40) -- (10.2,0.40) ;
    \draw    (10.2,0.40) -- (10.2,5.60) ;
    \draw    ( 2.4,5.60) -- (10.2,5.60) ;
    \draw    ( 2.6,5.80) -- (10.4,5.80) ;
    \draw    (10.4,0.60) -- (10.4,5.80) ;
    \draw    ( 2.8,6.00) -- (10.6,6.00) ;
    \draw    (10.6,0.80) -- (10.6,6.00) ;
    \draw    ( 2.6,5.60) -- ( 2.6,5.80) ;
    \draw    ( 2.8,5.80) -- ( 2.8,6.00) ;
    \draw    (10.2,0.60) -- (10.4,0.60) ;
    \draw    (10.4,0.80) -- (10.6,0.80) ;

    % Assistant Text
    \draw (3.16,0.72) node  [align=left] {\underline{{\footnotesize Assistant}}};

    %DB or Frigde
    \draw    (0.80,1.60) -- (1.00,1.40) -- (1.80,1.40) -- (1.60,1.60) -- (0.80,1.60) -- (0.80,5.00) -- (1.60,5.00) -- (1.60,1.60) -- (1.80,1.40) -- (1.80,4.80) -- (1.60,5.00);
    \draw (0.80,2.60) -- (1.60,2.60) ;
    %handles
    \draw (1.20,2.40) -- (1.50,2.40) ;
    \draw (1.20,2.80) -- (1.50,2.80) ;
    %Fridge Text
    \draw (1.20,3.20) node [align=left] {\tiny{Fridge}};

    % --- kitchen ---
    \draw (4.80,2.00) node [align=left] {\footnotesize{Kitchen}};
    %a kitchen sink to you is not a kitchen sink to me
    \draw (2.80,3.00) -- (3.40,2.20) -- (6.20,2.20) -- (6.80,3.00) -- (2.80,3.00) ;

    %Shape: Ellipse [id:dp15318352261434987] 
    \draw (3.54,2.76) ellipse (0.40 and 0.12); %front left
    \draw (3.68,2.44) ellipse (0.68 and 0.08); %back left
    \draw (4.50,2.44) ellipse (0.34 and 0.08); %back right
    \draw (4.50,2.76) ellipse (0.32 and 0.12); %front right

    \draw[rounded corners] (5.05,2.60) -- (5.00,2.30) -- (6.10,2.30) -- (6.50, 2.90) -- (3.10,2.90) -- (5.05,2.60);

    %recipe
    \draw (6.80,3.40) -- (6.80,5.20) -- (9.80,5.20) -- (9.80,3.80) -- (9.40,3.40) -- (9.40,3.80) -- (9.80,3.80);
    \draw (9.40,3.40) -- (9.20,3.40);
    \draw (9.20,3.80) -- (9.20,3.00) -- (8.20,3.00) -- (8.20,3.80) -- (9.20,3.80);
    \draw (8.00,3.40) -- (8.20,3.40);
    \draw (7.00,3.80) -- (7.00,3.00) -- (8.00,3.00) -- (8.00,3.80) -- (7.00,3.80);
    \draw (7.00,3.40) -- (6.80,3.40);

    \draw (8.30,4.60) node {\footnotesize{Recipe}};
    \draw (7.50,3.30) node {\footnotesize{Ingre-}};
    \draw (7.50,3.50) node {\footnotesize{dients}};
    \draw (7.50,4.00) node {\scriptsize{Input}};
    \draw (8.70,3.40) node {\footnotesize{Dish}};
    \draw (8.70,4.00) node {\scriptsize{Output}};

    %flavour
    \draw (8.60,0.80) -- (7.60,0.80) -- (7.60,2.40) -- (9.00,2.40) -- (9.00,1.20) -- (8.60,0.80) -- (8.60,1.20) -- (9.00,1.20);
    \draw (8.30,1.40) node {\footnotesize{Flavour}};
    \draw (8.30,1.76) node {\scriptsize{Parameters}};
    \draw (8.30,1.96) node {\scriptsize{Goal def.}};

    %Arrows
    \draw[<-, bend right=1.00, line width=0.04]  (2.00,2.40) to (3.00,2.40);
    \draw[->, bend left=1.00, line width=0.04]   (2.00,3.20) to (3.00,3.20);
    \draw[<-, bend right=1.00, line width=0.04]  (6.20,1.80) to (7.20,1.20);
    \draw[<-, bend left=1.00, line width=0.04]   (5.40,3.40) to (6.40,4.20);

    %Chef
    \draw (12.0,3.00) -- (15.0,3.00) -- (15.0,6.00) -- (12.0,6.00) -- (12.0,3.00);
    \draw (12.4,3.26) node {\underline{\footnotesize{Chef}}};
    \draw (13.2,3.26) node {\footnotesize{A}};
    \draw (13.8,3.26) node {\footnotesize{B}};
    \draw (14.4,3.26) node {\footnotesize{C}};
    \draw (13.0,4.00) node {\footnotesize{Recipe 3}};
    \draw (13.8,2.60) node {\footnotesize{Recipe 2}};
    \draw (13.0,5.20) node {\footnotesize{Recipe 1}};
    \draw (13.4,5.80) node {\small{.}};

    %dependency graph
    \draw (13.20,3.40) -- (12.96,3.80);
    \draw (13.80,3.40) -- (13.00,3.80);
    \draw (14.40,3.40) -- (13.08,3.80);
    \draw (13.06,4.20) -- (13.80,4.40);
    \draw (12.98,4.20) -- (13.98,5.00);
    \draw (13.00,5.40) -- (13.30,5.70);
    \draw (13.80,4.80) -- (13.44,5.70);

    %chef controls assistants
    \draw [<-, line width = 0.04] (10.8,4.60) -- (10.8,4.60);
    \draw [<-, line width = 0.04] (10.8,4.90) -- (10.8,4.90);
    \draw [<-, line width = 0.04] (10.8,4.30) -- (10.8,4.30);

    %parameter permutations
    \draw (15.4,3.40) -- (16.2,3.40) -- (16.6,3.80) -- (16.2,3.80) -- (16.2,3.40) -- (16.6,3.80) -- (16.6,6.00) -- (15.4,6.00) -- (15.4,3.40); 
    \draw (15.6,3.40) -- (15.6,3.20) -- (16.4,3.20) -- (16.8,3.60) -- (16.4,3.60) -- (16.4,3.20) -- (16.8,3.60) -- (16.8,5.80) -- (16.6,5.80);
    \draw (15.8,3.20) -- (15.8,3.00) -- (16.6,3.00) -- (17.0,3.40) -- (16.6,3.40) -- (16.6,3.00) -- (17.0,3.40) -- (17.0,5.60) -- (16.8,5.80);

    %text on parameter permutations
    \draw (16.0,4.70) node [align=left] {\tiny{num\_S}\\\tiny{num\_N}\\\tiny{data}\\\tiny{width}\\\tiny{height}};
    \draw[->, color=orange] (15.6,5.00) -- (14.4,4.56);
    \draw[->, color=orange] (15.6,5.30) -- (14.4,4.64);
    \draw[->, color=violet] (15.6,4.70) -- (15.6,4.04);
    \draw[->, color=violet] (15.6,4.40) -- (15.6,4.00);
    \draw[->, color=violet] (15.6,4.10) -- (15.6,3.96);
    \draw[->, color=cyan]   (15.6,5.30) -- (15.7,5.20);

    %parameter specification
    \draw (13.0,0.0) -- (17.0,0.0) -- (17.0,2.70) -- (13.0,2.70) -- (13.0,0.0);
    \node[below right] at (13.2,0.0) {\underline{\tiny{flavour.json}}};
    \node[below right] at (13.6,0.20) {\tiny{num\_S = 27}};
    \node[below right] at (13.6,0.40) {\tiny{num\_N = 42}};
    \node[below right] at (13.6,0.60) {\tiny{inputdata = ['input1.json','input2.json']}};
    \node[below right] at (13.2,1.00) {\underline{\tiny{input1.json}}};
    \node[below right] at (13.6,1.20) {\tiny{width = 120}};
    \node[below right] at (13.6,1.40) {\tiny{height = 34}};
    \node[below right] at (13.6,1.60) {\tiny{data = 'data.json'}};
    \node[below right] at (13.2,2.00) {\underline{\tiny{input2.json}}};
    \node[below right] at (13.8,2.10) {\tiny{\vdots}};
    \draw[->, bend left=0.10, line width=0.04] (15.0,2.00) to (15.6,3.10);
    \node at (15.6,2.40) {\tiny{Variation}};

The picture shows the components of the computing process.
In general, there is the fridge that stand for a database, multiple assistants who represents smaller programs or threads, the kitchen which is the processor the thread runs on and the chef.
As shown in the block of the chef, a simulation is divided into smaller computation steps.
There are dependencies between those steps and the parameters the steps take.
Those steps are called recipes.
The input of one recipe can be the output of another recipe or some input data.
The possibilities for input data for one simulation is defined in a .json file as shown to the right.
The chef produces every possible set and starts simulations each set of parameters.
Therefore, the parameters are further split up to start a simulation step only with the parameters needed for that step.
Not every ingredient is needed for every step in cooking, so the assistant only gets a list of relevant ingredients and a note concerning the flavour.
After an assistant is done, the prepared food goes into the fridge for another assistant to use.

To make sure, no meals are mixed up and nothing in the fridge gets confused, Chefkoch has got a unique namespace.
There is more than one meal ordered.
So the chef works parallel on all of them.

