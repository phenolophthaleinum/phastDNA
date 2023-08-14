const progress = document.getElementById("progress");
const circles = document.querySelectorAll(".circle");

let currentActive = 0;

let counter = 1;
let numDivs = document.querySelectorAll('.number');
let counterDiv = document.querySelector('#counter-div');
let num0 = document.getElementById('num0')
let num1 = document.getElementById('num1')

// counterDiv.addEventListener('click', () => {
//   numDivs[1].style.animation = 'slideUp 0.5s forwards'; // add animation dynamically
//   numDivs[1].addEventListener('animationend', () => {
//     numDivs[0].remove();
//     numDivs[1].style.animation = ''; // remove animation property
//     numDivs[1].classList.remove('next');
//     let newDiv = document.createElement('div');
//     newDiv.classList.add('number', 'next');
//     newDiv.style.top = '20px';
//     newDiv.textContent = ++counter;
//     counterDiv.appendChild(newDiv);
//     numDivs = document.querySelectorAll('.number');
//   });
// });
// let dir = true;
function count() {
    // let pHeight = num0.getBoundingClientRect().height;
    // var lineHeight = window.getComputedStyle(num0).getPropertyValue('line-height')
    // // var element = document.getElementById('image_1'),
    // // style = window.getComputedStyle(element),
    // // top = style.getPropertyValue('top');
    let tl = gsap.timeline();
    if (counter < 40) {
        counter++;
    }
    else {
        counter = 40;
    }
    num1.textContent = counter;
    // dir = !dir;
    tl.to(["#num0", "#num1"], {
        top: "-=200%",
        // top: dir ? "-=" + 2 * lineHeight + "px" : "+=" + 2 * lineHeight + "px",
        // top: `-${pHeight}px`,
        ease: Power3.easeInOut,
        duration: .9,
        // "--myBlur": 3,
        onComplete: swapNums
    });
    tl.to(["#num0", "#num1"], {
        ease: Power3.easeInOut,
        duration: 0.5,
        "--myBlur": 3,
    }, "<");
    tl.to(["#num0", "#num1"], {
        ease: Power3.easeInOut,
        duration: 0.35,
        "--myBlur": 0,
    }, 0.5);
}

function swapNums() {
    num0.textContent = counter;
    gsap.set(["#num0", "#num1"], {
        top: "+=200%",
        // top: "+=" + 2 * lineHeight + "px",
        // top: `+${pHeight}px`,
        duration: .9,
        "--myBlur": 0,
    })
}

// function count() {
//     if (counter < 40) {
//         counter++;
//     } else {
//         counter = 40;
//     }
//     num1.textContent = counter;

//     const fontSize = parseFloat(window.getComputedStyle(num0).getPropertyValue('font-size'));
//     const lineHeight = parseFloat(window.getComputedStyle(num0).getPropertyValue('line-height'));
//     // const topPosition = (-counter * lineHeight) / fontSize * 100 + '%';
//     const topPosition = -(lineHeight / fontSize) * 100 + '%';

//     gsap.to(["#num0", "#num1"], {
//         top: topPosition,
//         ease: Power3.easeInOut,
//         duration: 0.9,
//         onComplete: swapNums
//     });
// }

// function swapNums() {
//     num0.textContent = counter;
//     gsap.set(["#num0", "#num1"], {
//         top: '200%',
//         duration: 0
//     });
//     gsap.to(["#num0", "#num1"], {
//         top: '0%',
//         ease: Power3.easeInOut,
//         duration: 0.9
//     });
//     const fontSize = parseFloat(window.getComputedStyle(num0).getPropertyValue('font-size'));
//     const lineHeight = parseFloat(window.getComputedStyle(num0).getPropertyValue('line-height'));
//     // const topPosition = (-counter * lineHeight) / fontSize * 100 + '%';
//     const topPosition = -(lineHeight / fontSize) * 100 + '%';
//     gsap.set("#num0", {
//         top: topPosition,
//         duration: 0
//     });
// }

// function count() {
//     if (counter < 40) {
//         counter++;
//     } else {
//         counter = 40;
//     }
    
//     num1.textContent = counter;

//     const fontSize = parseFloat(window.getComputedStyle(num0).getPropertyValue('font-size'));
//     const lineHeight = parseFloat(window.getComputedStyle(num0).getPropertyValue('line-height'));

//     const topPosition = -((lineHeight / fontSize) * 100) + '%';

//     gsap.to(["#num0", "#num1"], {
//         top: topPosition,
//         ease: Power3.easeInOut,
//         duration: 0.9,
//         onComplete: swapNums
//     });
// }

// function swapNums() {
//     num0.textContent = counter;
//     gsap.set("#num0", { top: '0%' });
//     gsap.set("#num1", { top: '100%' });

//     // let temp = num0;
//     // num0 = num1;
//     // num1 = temp;
// }

// function count() {
//     let pHeight = num0.getBoundingClientRect().height; // Get the height of the div
//     if (counter < 40) {
//         counter++;
//     }
//     else {
//         counter = 40;
//     }
//     num1.textContent = counter;
//     gsap.to("#num0", {
//         top: `-${pHeight}px`,
//         ease: Power3.easeInOut,
//         duration: 0.9,
//         onComplete: swapNums
//     });

//     gsap.to("#num1", {
//         top: `-${pHeight}px`,
//         ease: Power3.easeInOut,
//         duration: 0.9
//     });
// }

// function swapNums() {
//     num0.textContent = counter;
//     gsap.set("#num0", {
//         top: `0px`
//     });
//     gsap.set("#num1", {
//         top: `${num1.getBoundingClientRect().height}px`,
//     });
// }

// let pHeight = num0.getBoundingClientRect().height; 
// function count() {
//     const sceneHeight = num0.clientHeight; // updating scene height before each count
//     if (counter < 40) {
//         counter++;
//     }
//     else {
//         counter = 40;
//     }
//     num1.textContent = counter;

//     gsap.to(["#num0", "#num1"], {
//         top: `-=${sceneHeight}px`,
//         ease: Power3.easeInOut,
//         duration: 0.9,
//         onComplete: swapNums,
//         onCompleteParams: [sceneHeight]
//     });
// }

// function swapNums(sceneHeight) {
//     num0.textContent = counter;
//     // const temp = num0;
//     // num0 = num1;
//     // num1 = temp;
//     num1.style.top = `${sceneHeight}px`;
// }


// num1.style.top = `${num0.clientHeight}px`; // Move num1 below num0 initially

// function count() {
//     if (counter < 40) {
//         counter++;
//     }
//     else {
//         counter = 40;
//     }
//     var tl = gsap.timeline({onComplete: swapNums});  // Create a GSAP timeline
//     num1.textContent = counter;

//     tl.to("#num0", {
//         top: `-=${num0.clientHeight}px`,
//         ease: Power3.easeInOut,
//         duration: 0.9,
//     }).to("#num1", {
//         top: `-=${num0.clientHeight}px`, //0
//         ease: Power3.easeInOut,
//         duration: 0.9
//     }, 0);  // The 2nd animation will start at the same time as the 1st
// }

// function swapNums() {
//     num0.textContent = counter;
//     gsap.set("#num0", {top: "0px"});
//     gsap.set("#num1", {top: `${num1.clientHeight}px`});
//     // var temp = num0;
//     // num0 = num1;
//     // num1 = temp;
// }

// function count() {
//     if (counter < 40) {
//         counter++;
//     } else {
//         counter = 40;
//     }

//     const fontSize = parseFloat(window.getComputedStyle(num0).getPropertyValue('font-size'));
//     const lineHeight = parseFloat(window.getComputedStyle(num0).getPropertyValue('line-height'));
//     const topPosition = (-counter * lineHeight) / fontSize + 'em';

//     num1.textContent = counter;

//     gsap.to(["#num0", "#num1"], {
//         top: topPosition,
//         ease: Power3.easeInOut,
//         duration: 0.9,
//         onComplete: swapNums
//     });
// }

// function swapNums() {
//     num0.textContent = counter;
//     gsap.set("#num0", {top: '0'});
//     gsap.set("#num1", {top: '100%'});

//     let temp = num0;
//     num0 = num1;
//     num1 = temp;
// }

counterDiv.addEventListener('click', () => {
    count();
});

circles.forEach((circle, index) => {
    circle.addEventListener("click", () => {
        currentActive = index
        updateStep();
    });
});

function updateStep() {
    circles.forEach((circle, index) => {
        // var spinner = circle.querySelector('.icon-circle');
        // console.log(index);
        // if (index < currentActive) {
        //     circle.classList.remove("active");
        //     circle.classList.add("done");
        //     // createCheck(circle);
        //     if (spinner){
        //         removeSpinner(spinner, () => createCheck(circle));
        //         // removeSpinner(spinner, circle);
        //         // createCheck(circle);
        //     }
        //     else {
        //         createCheck(circle);
        //     }
        // } 
        // else if (index == currentActive) {
        //     // circle.classList.add("active");
        //     circle.classList.add("active");
        //     circle.classList.remove('done');
        //     if (spinner){
        //         removeSpinner(spinner);
        //     }
        //     else {
        //         setTimeout(() => {
        //             createSpinner(circle);
        //           }, 400);
        //         // createSpinner(circle);
        //         removeCheck(circle);
        //     }
        // }
        // else {
        //     // console.log(spinner)
        //     circle.classList.remove("active");
        //     circle.classList.remove('done');
        //     if (spinner){
        //         removeSpinner(spinner);
        //     }
        //     else{
        //         removeCheck(circle);
        //     }
        //     // removeSpinner(spinner);
        // }

        // let checksToAnimate = [];
        var spinner = circle.querySelector('.icon-circle');
        var check = circle.querySelector('.done-check');

        if (index < currentActive) {
            // Circles before the current one - remove spinner, add check, and mark as done
            circle.classList.add("done");
            // circle.classList.add("error");
            circle.classList.remove("active");
            // if (index < currentActive) {
            //     // Circles before the current one - remove spinner, add check, and mark as done
            //     circle.classList.add("done");
            //     circle.classList.remove("active");
            //     if (spinner)
            //         removeSpinner(spinner, () => {
            //             if (!check) {
            //                 check = createCheck(circle);
            //                 checksToAnimate.push(check);
            //             }
            //         });
            //     else if (!check) {
            //         check = createCheck(circle);
            //         checksToAnimate.push(check);
            //     }
            // } 
            if (spinner)
            removeSpinner(spinner, () => {
                if (!check)
                    createCheck(circle);
                    // createError(circle);
            });
            else if (!check)
                createCheck(circle);

            // if (spinner)
            //     removeSpinner(spinner, () => {
            //         if (!check)
            //             setTimeout(() => createCheck(circle), 300);
            //     });
            // else if (!check)
            //     setTimeout(() => createCheck(circle), 300);
        }
        else if (index == currentActive) {
            // Current circle - ensure spinner is present, and remove check (if it exists) and done class
            circle.classList.add("active");
            circle.classList.remove('done');
            if (spinner == null)
                // createSpinner(circle)
                setTimeout(() => createSpinner(circle), 400);
            if (check)
                removeCheck(circle);
        }
        else {
            // Circles after the current one - remove both spinner and check, and "active" and "done" classes
            circle.classList.remove("active");
            circle.classList.remove('done');
            if (spinner)
                removeSpinner(spinner);
            if (check)
                removeCheck(circle);
        }

        // checksToAnimate.forEach(check => {
        //     gsap.fromTo(check, {
        //         opacity: 0,
        //         scale: 0
        //     }, {
        //         opacity: 1,
        //         scale: 1,
        //         duration: 0.3
        //     });
        // });
    });

    progress.style.width =
        ((currentActive) / (circles.length - 1)) * 100 + "%";
}

function createCheck(circleElem) {
    var check = `
    <i class="done-check bi bi-check-circle"></i>
    `;
    circleElem.innerHTML += check;
    // gsap.fromTo(".done-check", {
    //     opacity: 0,
    // },
    // {
    //     opacity: 1,
    //     duration: 0.3
    // });
}

function createError(circleElem) {
    var error = `
    <i class="error-x bi bi-x-circle"></i>
    `;
    circleElem.innerHTML += error;
}

function createSpinner(circleElem) {
    // var spinner = document.createElement('svg');
    // var spinner = document.createElement();
    // spinner.innerHTML = `
    // <path class="icon-path p1" pathLength="100" stroke-dasharray="100" stroke-dashoffset="-98"
    //     stroke-linecap="round" d="M 100 0 C 152 1 199 44 199 100 "
    //     stroke="#0ebeff" />
    // <path class="icon-path p2" d="M 100 199 C 152 199 199 156 199 100" pathLength="100"
    //     stroke-dasharray="100" stroke-dashoffset="98" stroke="#ae63e4"
    //     stroke-linecap="round" />
    // <path class="icon-path p3" d="M 0 100 C 1 152 44 199 100 199" pathLength="100"
    //     stroke-dasharray="100" stroke-dashoffset="98" stroke="#ffdd40"
    //     stroke-linecap="round" />
    // <path class="icon-path p4" d="M 100 0 C 44 1 1 44 0 100" pathLength="100"
    //     stroke-dasharray="100" stroke-dashoffset="98" stroke="#47cf73"
    //     stroke-linecap="round" />`;

    // spinner.setAttribute('class', 'icon-circle');
    // spinner.setAttribute('id', 'spinner');
    // spinner.setAttribute('viewBox', "0 0 200 200");
    var spinner = `
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg"
        viewBox="0 0 200 200" class="icon-circle" id="spinner">
        <path class="icon-path p1" pathLength="100" stroke-dasharray="100" stroke-dashoffset="-98"
            stroke-linecap="round" d="M 100 0 C 152 1 199 44 199 100 "
            stroke="#0ebeff" />
        <path class="icon-path p2" d="M 100 199 C 152 199 199 156 199 100" pathLength="100"
            stroke-dasharray="100" stroke-dashoffset="98" stroke="#ae63e4"
            stroke-linecap="round" />
        <path class="icon-path p3" d="M 0 100 C 1 152 44 199 100 199" pathLength="100"
            stroke-dasharray="100" stroke-dashoffset="98" stroke="#ffdd40"
            stroke-linecap="round" />
        <path class="icon-path p4" d="M 100 0 C 44 1 1 44 0 100" pathLength="100"
            stroke-dasharray="100" stroke-dashoffset="98" stroke="#47cf73"
            stroke-linecap="round" />
    </svg>`;
    // circleElem.appendChild(spinner);
    circleElem.innerHTML += spinner;
    gsap.fromTo(".icon-path", {
        opacity: 0,
    },
        {
            opacity: 1,
            duration: 0.3
        });
    pathAnim = gsap.to(".icon-path", {
        // opacity: 1,
        strokeDashoffset: 0,
        ease: "power3.inOut",
        yoyo: true,
        duration: 3,
        repeat: -1,
        stagger: {
            from: 1,
            amount: 0.4,
            axis: "x",
        },
        // x: 50,
    });
    spinnerRotation = gsap.to(".icon-circle", {
        rotate: 360,
        repeat: -1,
        duration: 2,
        ease: "linear",
        // yoyo: true,
    });
}

// function removeSpinner(spinnerElem) {
//     gsap.to(".icon-path", {
//         opacity: 0,
//         duration: 0.3,
//         onComplete: () => spinnerElem.remove()
//     });
//     // spinnerElem.remove();
// }

// function removeSpinner(spinnerElem, circleElem) {
//     gsap.to(".icon-path", {
//         opacity: 0,
//         duration: 0.3,
//         onComplete: () => {
//             spinnerElem.remove();
//             createSpinner(circleElem);
//         }
//     });
// }

function removeSpinner(spinnerElem, callback) {
    gsap.to(".icon-path", {
        opacity: 0,
        duration: 0.3,
        onComplete: () => {
            spinnerElem.remove();
            if (callback) callback();
        }
    });
}

function removeCheck(circleElem) {
    checkElem = circleElem.querySelector('.done-check');
    if (checkElem) {
        checkElem.remove();
    }
}

// pathAnim = gsap.to(".icon-path", {
//     // opacity: 0,
//     strokeDashoffset: 0,
//     ease: "power3.inOut",
//     yoyo: true,
//     duration: 3,
//     repeat: -1,
//     stagger: {
//       from: 1,
//       amount: 0.4,
//       axis: "x",
//     },
//     // x: 50,
//     });
//   spinnerRotation = gsap.to(".icon-circle", {
//   rotate: 360,
//   repeat: -1,
//   duration: 2,
//   ease: "linear",
//   // yoyo: true,
//   });