
// const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
// const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl))
var popoverList = []
var atest = document.getElementById("ajax-test");
var spinner = document.getElementById("spinner");
var task_name = document.getElementById("task-name").innerText;
var page_title = document.getElementsByTagName('title').innerText;
var anchor = document.querySelector(".anchor");
const progress = document.getElementById("progress");
const circles = document.querySelectorAll(".circle");
const error_regex = new RegExp("(.+ERROR)[\s\S]*", 'gm');
var overflowing = false;
let currentActive = 0;
let counter = 0;
let counterSet = false;
let num0 = document.getElementById('num0')
let num1 = document.getElementById('num1')
let currentProgress = 'No data yet.';

// events = {
//   'Reading metadata': {
//     'code': 0
//   },
//   'Sampling': {
//     'code': 1
//   },
//   'Labelling': {
//     'code': 2
//   },
//   'Sampling sequences': {
//     'code': 3
//   },
//   'Running fastDNA-supervised': {
//     'code': 4
//   },
//   'Running fastDNA-predict': {
//     'code': 5
//   },
//   'Scoring': {
//     'code': 6
//   }
// }

function count() {
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

function updateStep(status) {
  popoverList.forEach((popover) => {
    popover.dispose()
  });
  popoverList = [];
  circles.forEach((circle, index) => {
      var spinner = circle.querySelector('.icon-circle');
      var check = circle.querySelector('.done-check');

      if (status === -1) {
        // Handle error status
        circle.classList.remove("active");
        if (check)
            return;
        // if (spinner == null)
        //     createError(circle);
        if (spinner) {
            removeSpinner(spinner, () => {
                createError(circle);
            });
            circle.classList.add("error");
        }
        // Exit the program
        return;
      }

      if (status === 0 && index === circles.length - 1) {
        // Handle success status on the last circle
        circle.classList.add("done");
        circle.classList.remove("active");
        if (spinner)
            removeSpinner(spinner, () => {
                if (!check)
                    createCheck(circle);
            });
        return;
      }

      if (index < currentActive) {
          // Circles before the current one - remove spinner, add check, and mark as done
          circle.classList.add("done");
          // circle.classList.add("error");
          circle.classList.remove("active");
          console.log(popoverList);
          if (spinner)
          removeSpinner(spinner, () => {
              if (!check)
                  createCheck(circle);
                  // createError(circle);
          });
          else if (!check)
              createCheck(circle);
      }
      else if (index == currentActive) {
          // Current circle - ensure spinner is present, and remove check (if it exists) and done class
          circle.classList.add("active");
          circle.classList.remove('done');
          circle.setAttribute("data-bs-toggle", "popover");
          circle.setAttribute("data-bs-placement", "top");
          circle.setAttribute("data-bs-content", currentProgress);
          circle.setAttribute("data-bs-trigger", "hover");
          // const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
// const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl))
          popoverList.push(new bootstrap.Popover(circle));
          if (spinner == null)
              // createSpinner(circle)
              setTimeout(() => createSpinner(circle), 400);
          if (check)
              removeCheck(circle);
        //   if (status === 0)
        //   removeSpinner(spinner, () => {
        //     if (!check)
        //         createCheck(circle);
        //         // createError(circle);
        // });
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
  });

  progress.style.width =
      ((currentActive) / (circles.length - 1)) * 100 + "%";
}

function createCheck(circleElem) {
  var check = `
  <i class="done-check bi bi-check-circle"></i>
  `;
  circleElem.innerHTML += check;
}

function createError(circleElem) {
  var error = `
  <i class="error-x bi bi-x-circle"></i>
  `;
  circleElem.innerHTML += error;
}

function createSpinner(circleElem) {
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

function isOverflowing(elem) {
  return elem.scrollHeight > elem.clientHeight;
}

pathAnim = gsap.to(".icon-path", {
  // opacity: 0,
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
spinnerRotation = gsap.to(".icon", {
rotate: 360,
repeat: -1,
duration: 2,
ease: "linear",
// yoyo: true,
});
var interval = setInterval(function() {
  $.ajax({
    url: `/test/${task_name}`,
    type: 'GET',
    tryCount: 0,
    retryLimit: 10,
    success: function(response) {
      console.log(response['status']);
      if (response['status'] === -1){
        document.title = "phastDNA: task failed"
        clearInterval(interval);
      }
      if (response['status'] === 0){
        document.title = "phastDNA: task successful"
        clearInterval(interval)
      }
      event_id = response['run_info']['event_id'];
      progress_value = response['run_info']['progress'];
      if (event_id){
        currentActive = event_id;
        currentProgress = 'No data yet.';
        updateStep(response['status']);
      }
      else if (progress_value){
        currentProgress = progress_value;
        updateStep();
      }
      else if (response['status'] < 1){
        updateStep(response['status']);
      }

      if (response['run_info']['iter'])
      {
        if (!counterSet) {
          counter = response['run_info']['iter'] - 1;
          counterSet = true;
        }
        count();
      }
      // atest.innerText = response['content'];
      if (response['status'] === 0){
        console.log(response['status']);
        var normalPara = document.createElement("p");
        var successPara = document.createElement("p");
        successPara.classList.add("fade-in", "status-success");
        normalPara.classList.add("fade-in");
        response_split = response['content'].split('\n');
        successPara.innerText = response_split.at(-2);
        normalPara.innerText = response_split.slice(0, -2).join('\n');
        // atest.appendChild(normalPara);
        // atest.appendChild(successPara);
        atest.insertBefore(normalPara, anchor);
        atest.insertBefore(successPara, anchor);
        // atest.lastElementChild.scrollIntoView({ behavior: 'smooth', block: 'end' });
      //   atest.animate({
      //     scrollTop: atest.prop("scrollHeight")
      // }, 500);
      // atest.scrollTop = atest.scrollHeight;
        if (!overflowing) {
          overflowing = isOverflowing(atest);
          atest.scrollTop = atest.scrollHeight;
        }
      }
      else if (response['status'] === -1){
        console.log(response['status']);
        var normalPara = document.createElement("p");
        var successPara = document.createElement("p");
        successPara.classList.add("fade-in", "status-error");
        normalPara.classList.add("fade-in");
        response_split = response['content'].split(error_regex);
        // successPara.innerText = response_split.at(-2);
        // console.log(response['content'].split(error_regex).slice(-2).join(''));
        successPara.innerText = response_split.slice(-2).join('');
        normalPara.innerText = response_split.slice(0, -2);
        console.log(response_split.slice(0))
        // atest.appendChild(normalPara);
        // atest.appendChild(successPara);
        atest.insertBefore(normalPara, anchor);
        atest.insertBefore(successPara, anchor);
        // atest.lastElementChild.scrollIntoView({ behavior: 'smooth', block: 'end' });
      //   atest.animate({
      //     scrollTop: atest.prop("scrollHeight")
      // }, 500);
      // atest.scrollTop = atest.scrollHeight;
        if (!overflowing) {
          overflowing = isOverflowing(atest);
          atest.scrollTop = atest.scrollHeight;
        }
      }
      else {
        // console.log(response['content']);
        console.log(response['run_info']);
        var para = document.createElement("p");
        para.innerText = response['content'];
        para.classList.add('fade-in');
        // atest.appendChild(para);
        atest.insertBefore(para, anchor);
        // atest.lastElementChild.scrollIntoView({ behavior: 'smooth', block: 'end' });
      //   atest.animate({
      //     scrollTop: atest.prop("scrollHeight")
      // }, 500);
      // atest.scrollTop = atest.scrollHeight;
        if (!overflowing) {
          overflowing = isOverflowing(atest);
          atest.scrollTop = atest.scrollHeight;
        }
      }
      // atest.innerHTML += `<p>${response['content']}</p><br>`;

    },
    error: function(xhr) {
        alert(xhr.responseText);
    }
  });
}, 2000);