var param_btn = document.getElementById('offcanvas-params-btn');
var run_pred_btn = document.getElementById('post-predict-button');
var run_train_btn = document.getElementById('post-train-button');
var setup = document.getElementById('current-setup');
var threads_slider_predict = document.getElementById('predict-fastdna-threads');
var threads_slider_train = document.getElementById('train-fastdna-threads');
var minn_slider = document.getElementById('train-training-minn');
var maxn_slider = document.getElementById('train-training-maxn');
var max_threads = window.navigator.hardwareConcurrency;
threads_slider_predict.max = max_threads;
threads_slider_train.max = max_threads;
var threads_num_predict = document.getElementById('predict-threads-num');
var threads_num_train = document.getElementById('train-threads-num');
var minn_num = document.getElementById('minn-num');
var maxn_num = document.getElementById('maxn-num');
threads_num_predict.innerText = threads_slider_predict.value;
threads_num_train.innerText = threads_slider_train.value;
// console.log(threads_num);
var predict_form = document.getElementById('predict-form');
console.log(predict_form);
var train_form = document.getElementById('train-form');
console.log(train_form);
var currentTab = document.getElementById('pills-home-tab');
var currentToasts = document.getElementsByClassName('.toast');
var tax_dropdown = document.getElementById('train-opt-filter')
var label_dropdown = document.getElementById('train-opt-filterLabel')
// const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
// const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
params = {
  'pills-predict-tab': {
    'predict-path-output': "Output path",
    'predict-path-classifier': "Classifier path",
    'predict-path-virus': "Viruses path",
    'predict-fastdna-path': "fastDNA path",
    'predict-fastdna-threads': 'Threads',
    'predict-fastdna-hits': "Considered hits"
  },
  'pills-train-tab': {
    'train-path-output': "Output path",
    'train-path-host': "Hosts path",
    'train-path-virus': "Viruses path",
    'train-fastdna-path': 'fastDNA path',
    'train-fastdna-threads': 'Threads',
    'train-training-dim': 'Word vector size',
    'train-training-minn': 'Minimum k-mer size',
    'train-training-maxn': 'Maximum k-mer size',
    'train-training-readlen': 'Read length',
    'train-training-readnum': 'Read samples number',
    'train-training-lr': 'Learning rate',
    'train-training-ulr': 'Learning rate update rate',
    'train-training-epoch': 'Epochs number',
    'train-training-loss': 'Loss function',
    'train-opt-preiter': 'Pre-iterations number',
    'train-opt-iter': 'Iterations number',
    'train-opt-hits': 'Considered hits',
    'train-opt-filter': 'Data filter',
    'train-opt-filterLabel': "Label filter",
    'train-opt-reps': 'Representatives number',
  }
}
tabs = {
  'pills-home-tab': "Home",
  'pills-predict-tab': "Predict",
  'pills-train-tab': "Train"
}

// check if loaded: probably unecessary
// document.addEventListener("readystatechange", (event) => {
//   if (event.target.readyState === "interactive") {
//     console.log('loading-interactive');
//   } else if (event.target.readyState === "complete") {
//     console.log('done loading');
//   }
// });

param_btn.onclick = function () {
  setup.innerHTML = '';
  for (const [key, val] of Object.entries(params[currentTab])) {
    var elem = document.getElementById(key);
    if (elem && elem.value !== "") {
      var elem_value = elem.value;
      // var entry = document.createElement('h6');
      // entry.innerText = `${val}: ${elem_value}`;
      var entry = document.createElement('div')
      // entry.className = 'list-group-item';
      entry.classList.add('list-group-item', 'glass');
      entry.innerHTML = `<div class="d-flex w-100 justify-content-between">
                            <h5 class="mb-1 flavor-5">${val}</h5>
                          </div>
                          <p class="mb-1 dynamic-break flavor-visibility">${elem_value}</p>`;
      setup.appendChild(entry);
    }
    else {
      continue;
    }
  }
  if (setup.innerHTML === '') {
    setup.innerHTML = `<h5>No parameters has been set.</h5>`;
  }
  // output = document.getElementById('input-path-output').value
  // var output_entry = document.createElement('h6');
  // output_entry.id = 'output-path-entry';
  // output_entry.innerText = `${params['input-path-output']}: ${output}`;
  // console.log(output);
  // setup.appendChild(output_entry);
}

// function hideIcon() {
//   var param_icon = document.getElementById('offcanvas-params-btn-icon');
//   param_icon.style.display = "none";
// }

// gsap.set("#offcanvas-params-btn-icon", {
//   display: 'none',
//   opacity: 0
// })

// gsap.set(".red-test", {
//   // display: 'none',
//   left: -1000
// })

// var btn_icon_anim = gsap.to("#offcanvas-params-btn-icon", .2, {
//   display: 'inline',
//   opacity: 1,
//   ease: "power1.inOut",
// });
param_btn.addEventListener('mouseover', (e) => {
  // gsap.to("#offcanvas-params-btn-label", .2, {
  //   x: -20,
  //   ease: "power1.inOut",
  // });
  // btn_icon_anim.play();
  gsap.to("#offcanvas-params-btn-icon", .2, {
    // display: 'inline',
    // transform: 'scale(1)',
    opacity: 1,
    fontSize: 18,
    // force3D: true,
    ease: "power1.inOut",
  });
  // gsap.to("#offcanvas-params-btn", .2, {
  //   width: 300,
  //   ease: "power1.inOut",
  // });
  // console.log(param_btn.style.width);
});

param_btn.addEventListener('mouseleave', (e) => {
  // gsap.to("#offcanvas-params-btn-label", .2, {
  //   x: -20,
  //   ease: "power1.inOut",
  // });
  // btn_icon_anim.reverse();
  // gsap.to("#offcanvas-params-btn", 0.2, {
  //   width: 275,
  //   ease: "power1.inOut",
  // });
  gsap.to("#offcanvas-params-btn-icon", .2, {
    opacity: 0,
    fontSize: 0,
    // force3D: true,
    ease: "power1.inOut",
  });
  // gsap.to("#offcanvas-params-btn-icon", .25, {
  //   // transform: 'scale(0)',
  //   // display: 'none',
  //   delay: .25,
  // });
  // console.log(param_btn.style.width);
});

// run_train_btn.addEventListener('mouseenter', () => {
//   console.log(run_train_btn.getBoundingClientRect())
//   var targetOffset = run_train_btn.getBoundingClientRect().width;
//   gsap.to('.btn-label', .3, {
//     // transformOrigin: "center center",
//     left: targetOffset,
//     ease: "power1.inOut",
//     force3D: true,
//   });
//   gsap.to('.red-test', .3, {
//     // transformOrigin: "center center",
//     // x: 8,
//     left: '50%',
//     ease: "power1.inOut",
//     force3D: true,
//   });
// })

// run_train_btn.addEventListener('mouseleave', () => {
//   // console.log('train button enter')
//   var targetOffset = run_train_btn.getBoundingClientRect().width;
//   gsap.to('.btn-label', .3, {
//     // transformOrigin: "center center",
//     // x: -8,
//     left: 0,
//     ease: "power1.inOut",
//     force3D: true,
//   });
//   gsap.to('.red-test', .3, {
//     // transformOrigin: "center center",
//     // x: -targetOffset,
//     left: -targetOffset,
//     ease: "power1.inOut",
//     force3D: true,
//   });
// })


Array.from(document.querySelectorAll(".run-btn")).forEach(btn => {
  gsap.set(".red-test", {
    // display: 'none',
    left: -1000,

  })
  btn.addEventListener('mouseenter', () => {
    var targetOffset = btn.getBoundingClientRect().width;
    gsap.to('.btn-label', .3, {
      // transformOrigin: "center center",
      left: targetOffset,
      ease: "power1.inOut",
      // force3D: true,
    });
    gsap.to('.red-test', .3, {
      // transformOrigin: "center center",
      // x: 8,
      left: '50%',
      ease: "power1.inOut",
      // force3D: true,
    });
  });
  btn.addEventListener('mouseleave', () => {
    // console.log('train button enter')
    var targetOffset = btn.getBoundingClientRect().width;
    gsap.to('.btn-label', .3, {
      // transformOrigin: "center center",
      // x: -8,
      left: 0,
      ease: "power1.inOut",
      // force3D: true,
    });
    gsap.to('.red-test', .3, {
      // transformOrigin: "center center",
      // x: -targetOffset,
      left: -targetOffset,
      ease: "power1.inOut",
      // force3D: true,
    });
  });
});



var hometab = document.getElementById('pills-home-tab')
console.log(hometab.ariaSelected)

function test() {
  console.log(clicked)
}

// const hometab_obj = document.getElementsByClassName('nav-item');
// for (const elem of hometab_obj) {
//     if (elem.id == "pills-home-tab") {
//         hometab_obj.addEventListener('click', test);   
//     }
//     else {
//         console.log("not home");
//     }
// }

gsap.set(".btn-primary", {
  y: 60,
});

function hideParamButton() {
  param_btn.style.display = "none";
}

function hideRunButton() {
  run_btn.style.display = "none";
}
function showButton(){
  param_btn.style.display = "block";
  // run_pred_btn.disabled = false;
  // run_train_btn.disabled = false;
  // param_btn.disabled = false;
}

window.onload = function () {
  var tabEl = document.querySelectorAll('button[data-bs-toggle="pill"]')
  tabEl.forEach(function (el) {
    el.addEventListener('shown.bs.tab', function (event) {
      console.log(event.target.id); // newly activated tab
      if (['pills-home-tab', 'pills-task-tab'].includes(event.target.id)) {
        // param_btn.style.display = "none";
        // gsap.to(param_btn, {
        //   y: 60,
        //   opacity: 0,
        //   ease: "power1.inOut",
        //   force3D: true,
        //   onComplete: hideParamButton,
        //   duration: 0.2
        // })
        gsap.to(".btn-primary", {
          y: 60,
          opacity: 0,
          force3D: true,
          stagger: {
            each: 0.1,
            ease: "power1.inOut",
            onComplete: function () {
              this.targets()[0].style.display = "none";
              // run_pred_btn.disabled = true;
              // run_train_btn.disabled = true;
              // param_btn.disabled = true;
            }
          },
          // onComplete: hideRunButton,
          duration: 0.2
        })
        currentTab = 'pills-home-tab';
      }
      else {
        if (event.target.id === 'pills-predict-tab') {
          // param_btn.style.display = "block";
          run_pred_btn.style.display = "block";
          run_train_btn.style.display = "none";
          // run_pred_btn.disabled = false;
          // param_btn.disabled = false;
          currentTab = 'pills-predict-tab';
          // run_btn.form = predict_form;
          // document.getElementById("post-button").form = document.getElementById("predict-form");
          // console.log(document.getElementById("post-button").form);
        }
        if (event.target.id === 'pills-train-tab') {
          // param_btn.style.display = "block";
          run_train_btn.style.display = "block";
          run_pred_btn.style.display = "none";
          // run_train_btn.disabled = false;
          // param_btn.disabled = false;
          currentTab = 'pills-train-tab';
          // document.getElementById("post-button").form = document.getElementById("train-form");
          // console.log(document.getElementById("post-button").form);
        }
        // gsap.to(param_btn, {
        //   y: 0,
        //   opacity: 1,
        //   duration: 0.2,
        //   ease: "power1.inOut",
        //   force3D: true,
        // })
        
        gsap.to(".btn-primary", {
          onStart: showButton,
          y: 0,
          opacity: 1,
          duration: 0.2,
          force3D: true,
          stagger: {
            each: 0.1,
            ease: "power1.inOut",
            // onComplete: function() {
            //   this.targets()[0].style.display = "block";
            // }
          },
        })

        // if (event.target.id === 'pills-predict-tab') {

        //   // run_btn.form = predict_form;
        //   // document.getElementById("post-button").form = document.getElementById("predict-form");
        //   // console.log(document.getElementById("post-button").form);
        // }
        // if (event.target.id === 'pills-train-tab') {
        //   // document.getElementById("post-button").form = document.getElementById("train-form");
        //   // console.log(document.getElementById("post-button").form);
        // }
      }
      // event.relatedTarget // previous active tab
    })
  })
}

// const tabEl = document.querySelector('button[data-bs-target="#pills-home"]')
// tabEl.addEventListener('shown.bs.tab', event => {
//     if (param_btn.style.display === "none") {
//         param_btn.style.display = "block";
//       } else {
//         param_btn.style.display = "none";
//       }
// //   event.target // newly activated tab
// //   console.log(event.target.clicked)
// //   event.relatedTarget // previous active tab
// })

threads_slider_predict.addEventListener('input', (e) => {
  threads_num_predict.textContent = e.target.value;
})

threads_slider_train.addEventListener('input', (e) => {
  threads_num_train.textContent = e.target.value;
})

minn_slider.addEventListener('input', (e) => {
  minn_num.textContent = e.target.value;
})

maxn_slider.addEventListener('input', (e) => {
  maxn_num.textContent = e.target.value;
})


// console.log(window.navigator.hardwareConcurrency);
// console.log(document.getElementById('input-fastdna-threads').max);



//something about form validation form bootstrap idk
// (() => {
//   'use strict'

//   // Fetch all the forms we want to apply custom Bootstrap validation styles to
//   const forms = document.querySelectorAll('.needs-validation')

//   // Loop over them and prevent submission
//   Array.from(forms).forEach(form => {
//     form.addEventListener('submit', event => {
//       if (!form.checkValidity()) {
//         event.preventDefault()
//         event.stopPropagation()
//       }

//       form.classList.add('was-validated')
//     }, false)
//   })
// })()

function findAncestor(el, cls) {
  while ((el = el.parentElement) && !el.classList.contains(cls));
  return el;
}
// const inputs_predict = document.getElementById("pills-predict").querySelectorAll('input')
// console.log(inputs_predict)
// dot indicator (not working well and kinda not intuitive)
// Array.from(inputs_predict).forEach(input => {
//   input.addEventListener('change', (e) => {
//     console.log(window.getComputedStyle(input, ':invalid'));
//     if (window.getComputedStyle(input, ':invalid').content !== 'none') {
//       const path = []
//       while (input) {
//         if (input.className === 'accordion-item') {
//           var i = input.querySelectorAll('span');
//           console.log(i);
//           i[0].style.display = "block"
//           break;
//         }
//         path.push(input)
//         input = input.parentElement
//       }
//     }
//     else {
//       const path = []
//       while (input) {
//         if (input.className === 'accordion-item') {
//           var i = input.querySelectorAll('span');
//           console.log(i);
//           i[0].style.display = "none"
//           break;
//         }
//         path.push(input)
//         input = input.parentElement
//       }
//     }
//     // console.log(path)
//     // badge = findAncestor('input', 'badge')
//     // console.log(badge);
//   })
// })
// let invalid_sections = (function() {
//   let set = new Set();
//   return {
//     add: function(value) { set.add(value); },
//     clear: function() { set.clear(); },
//     getValues: function() { return set; }
//   };
// })();

// console.log(document.getElementsByClassName('toast-container'));
// let invalid_sections = new Set();
// Array.from(inputs_predict).forEach(input => {
//   toast_container.innerHTML = '';
//   input.addEventListener('invalid', (e) => {
//     // console.log(input.labels[0].textContent)
//     // let invalidSections = invalid_sections;

//     while (input) {
//       if (input.className === 'accordion-item') {
//         var i = input.querySelectorAll('h2.accordion-header')[0].innerText;
//         console.log(typeof i);
//         var t = document.createElement('div')
//         t.id = `${i.replace(/ /g, "-")}`
//         t.classList = 'toast'
//         t.role = 'alert'
//         t.ariaAtomic = 'true';
//         t.ariaLive = 'assertive';
//         //<div id="liveToast" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
//         t.innerHTML = `
//     <div class="toast-header">
//         <!-- <img src="..." class="rounded me-2" alt="..."> -->
//         <i class="bi bi-exclamation-triangle-fill flex-shrink-0 me-2"></i>
//         <strong class="me-auto">Error</strong>
//         <!-- <small>11 mins ago</small> -->
//         <button type="button" class="btn-close" data-bs-dismiss="toast"
//             aria-label="Close"></button>
//     </div>
//     <div class="toast-body">
//         <p>${i} has invalid fields.</p>
//     </div>
// </div>`;
//         toast_container.appendChild(t);
//         // console.log(invalidSections.add(i));
//         // i[0].style.display = "block"
//         break;
//       }
//       input = input.parentElement
//     }

//     // invalid_sections = invalidSections;
//     // console.log(document.querySelectorAll('.toast')[0].querySelector('.toast-body'))
//     // var toastElList = [].slice.call(document.querySelectorAll('.toast'))
//     // var toastList = toastElList.map(function(toastEl) {
//     //   toastEl.querySelector('p').textContent = `${i} has invalid fields.`
//     //   return new bootstrap.Toast(toastEl)
//     // })
//     // toastList.forEach(toast => {
//     //   // console.log(toast.querySelector('.toast-body'))
//     //   toast.show()
//     // })
//     // console.log(input.querySelector('h3'))
//     // console.log(window.getComputedStyle(input, ':invalid'));
//     // console.log(path)
//     // badge = findAncestor('input', 'badge')
//     // console.log(badge);
//   })
// })
let toast_container = document.getElementsByClassName('toast-container')[0];
Array.from(document.querySelectorAll(".run-btn")).forEach(btn => {
  btn.addEventListener("click", (e) => {
    let targetForm = btn.id === "post-predict-button" ? "predict-form" : "train-form";
    // let toast_containers = document.getElementsByClassName('toast-container');
    // let toast_container = currentTab === "pills-predict-tab" ? toast_containers[0] : toast_containers[1];
    // if (currentTab === "pills-predict-tab"){
    //   toast_container = document.getElementById('predict-toasts');
    // }
    // if (currentTab === "pills-train-tab") {
    //   toast_container = document.getElementById('train-toasts');
    // }
    // console.log(`current container: ${toast_container}`);
    // currentToasts = document.getElementsByClassName('.toast');
    let invalid_sections = new Set();
    // invalid_sections.add(1);
    // console.log(toast_container);
    // console.log(invalid_sections);
    toast_container.innerHTML = '';
    let invalidInputs = document.getElementById(targetForm).querySelectorAll(':invalid')
    console.log(invalidInputs);

    Array.from(invalidInputs).forEach(invalid => {
      while (invalid) {
        if (invalid.className === 'accordion-item') {
          var i = invalid.querySelectorAll('h2.accordion-header')[0].innerText;
          console.log(typeof i);
          invalid_sections.add(i);
          // i[0].style.display = "block"
          break;
        }
        invalid = invalid.parentElement
      }
    })
    console.log(invalid_sections);

    invalid_sections.forEach(section => {
      console.log(section)
      var t = document.createElement('div')
      t.id = 'liveToast'
      t.classList = 'toast'
      t.role = 'alert'
      t.ariaAtomic = 'true';
      t.ariaLive = 'assertive';
      //<div id="liveToast" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
      t.innerHTML = `
      <div class="toast-header">
          <!-- <img src="..." class="rounded me-2" alt="..."> -->
          <i class="bi bi-exclamation-triangle-fill flex-shrink-0 me-2"></i>
          <strong class="me-auto">Error</strong>
          <!-- <small>11 mins ago</small> -->
          <button type="button" class="btn-close" data-bs-dismiss="toast"
              aria-label="Close"></button>
      </div>
      <div class="toast-body">
          <h3>${tabs[currentTab]}:</h3>
          <p>${section} has invalid fields.</p>
      </div>
  </div>`;
      toast_container.appendChild(t);
    })

    console.log(toast_container)
    console.log(document.querySelectorAll('.toast'))
    var toastElList = [].slice.call(document.querySelectorAll('.toast'))
    console.log(toastElList)
    var toastList = toastElList.map(function (toastEl) {
      return new bootstrap.Toast(toastEl)
    })
    toastList.forEach(toast => {
      // console.log(toast.querySelector('.toast-body'))
      toast.show()
    })
  })
})

// Array.from(currentToasts).forEach(t => {
//   t.addEventListener('hidden.bs.toast', () => {
//     console.log('kupa')
//   })
// })
//old toasts
// document.getElementById('post-button').addEventListener("click", (e) => {
//   let invalid_sections = new Set();
//   // invalid_sections.add(1);
//   // console.log(toast_container);
//   // console.log(invalid_sections);
//   toast_container.innerHTML = '';
//   let invalidInputs = document.getElementById("predict-form").querySelectorAll(':invalid')
//   console.log(invalidInputs);

//   Array.from(invalidInputs).forEach(invalid => {
//     while (invalid) {
//       if (invalid.className === 'accordion-item') {
//         var i = invalid.querySelectorAll('h2.accordion-header')[0].innerText;
//         console.log(typeof i);
//         invalid_sections.add(i);
//         // i[0].style.display = "block"
//         break;
//       }
//       invalid = invalid.parentElement
//     }
//   })
//   console.log(invalid_sections);

//   invalid_sections.forEach(section => {
//     console.log(section)
//     var t = document.createElement('div')
//     t.id = 'liveToast'
//     t.classList = 'toast'
//     t.role = 'alert'
//     t.ariaAtomic = 'true';
//     t.ariaLive = 'assertive';
//     //<div id="liveToast" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
//     t.innerHTML = `
//       <div class="toast-header">
//           <!-- <img src="..." class="rounded me-2" alt="..."> -->
//           <i class="bi bi-exclamation-triangle-fill flex-shrink-0 me-2"></i>
//           <strong class="me-auto">Error</strong>
//           <!-- <small>11 mins ago</small> -->
//           <button type="button" class="btn-close" data-bs-dismiss="toast"
//               aria-label="Close"></button>
//       </div>
//       <div class="toast-body">
//           <p>${section} has invalid fields.</p>
//       </div>
//   </div>`;
//     toast_container.appendChild(t);
//   })

//   console.log(toast_container)
//   console.log(document.querySelectorAll('.toast'))
//   var toastElList = [].slice.call(document.querySelectorAll('.toast'))
//   console.log(toastElList)
//   var toastList = toastElList.map(function (toastEl) {
//     return new bootstrap.Toast(toastEl)
//   })
//   toastList.forEach(toast => {
//     // console.log(toast.querySelector('.toast-body'))
//     toast.show()
//   })

// })


// useless focusing on element from toast
// document.getElementById("toast-target").addEventListener("click", () => {
//   document.getElementById("input-path-output").focus();
// })


//potential info icon move on info open
// var info_output_text = document.getElementById('outputInfoText');
// function addToInfo(infoText, targetIcon){
//   infoText.appendChild(targetIcon);
// }

// var info_btn = document.getElementById('info-output');
// info_btn.addEventListener('click', (e) => {
//   target = e.target;
//   console.log(target);
//   gsap.to(target, {
//     y: 65,
//     x: -150,
//     // opacity: 0,
//     ease: "power1.inOut",
//     force3D: true,
//     onComplete: addToInfo(info_output_text, target),
//     duration: 0.2
//   })
// })

//ajax
// $(document).ready(function() {
//   setInterval("ajaxd()", 5000); // call every 10 seconds
// });

// function ajaxd() {
//   //reload result into element with id "sysStatus"
//   console.log("/test");
// };

// var atest = document.getElementById("ajax-test");
// setInterval(function() {
//   $.ajax({
//     url: "/test",
//     type: 'GET',
//     success: function(response) {
//       atest.innerText = response;
//     },
//     error: function(xhr) {
//       alert("XHR error");
//     }
//   });
// }, 5000);


// ====== potential dropdown arrow Animation, not very good though

// Array.from(document.querySelectorAll(".form-select")).forEach(select => {
//   select.addEventListener('click', () => {
//     select.classList.contains('selectdropdown-active') ? select.classList.remove('selectdropdown-active') : select.classList.add('selectdropdown-active');
//   })
// })

// const accordionElement = document.getElementsByClassName('accordion-collapse');
// console.log(accordionElement);

// accordionElement.addEventListener('shown.bs.collapse', function (event) {
//   // code to run after accordion item is shown
// //   console.log('Accordion item shown!');
// //   console.log(event.target.previousElementSibling);
//   event.target.previousElementSibling.scrollIntoView({ behavior: "smooth", block: "start", inline: "nearest"});

// });

// accordionElement.addEventListener('hide.bs.collapse', function (event) {
//     // code to run after accordion item is shown
//   //   console.log('Accordion item shown!');
//   //   console.log(event.target.previousElementSibling);
//     scrollTo({top: 100, behavior: "smooth"});
//     // document.scrollIntoView({ behavior: "smooth", block: "start", inline: "nearest"});
  
// });

tax_dropdown.addEventListener('change', (e) => {
  // console.log(`label dropdown val: ${e.target.value}`);
  // console.log(`label dropdown idx: ${label_dropdown.selectedIndex}`);
  for (let i = 0; i < label_dropdown.options.length; i++) {
    if (label_dropdown.options[i].value === e.target.value) {
      label_dropdown.selectedIndex = i;
      break;
    }
  }
})