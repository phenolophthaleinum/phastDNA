class DefaultDict {
  constructor(defaultValueFunc) {
    return new Proxy({}, {
      get: (target, new_key) => new_key in target ? 
        target[new_key] : 
        (target[new_key] = typeof defaultValueFunc === 'function' ? 
          new DefaultDict(defaultValueFunc) : defaultValueFunc)
    });
  }
}
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
let currentIter = null;
let accordionIters = document.getElementById("accordionIters");
let iterationData = new DefaultDict(Object);
var bestScore = 0;
// var bestBadge = null;

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
  if (counter < 9999) {
      counter++;
  }
  else {
      counter = 9999;
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
          // console.log(popoverList);
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
          circle.setAttribute("data-bs-html", "true");
          circle.setAttribute("data-bs-placement", "top");
          circle.setAttribute("data-bs-title", "Step progress");
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
      fastdna_progress = response['run_info']['fastdna']['progress'];
      if (event_id){
        currentActive = event_id;
        currentProgress = 'No data yet.';
        updateStep(response['status']);
      }
      else if (progress_value){
        currentProgress = progress_value;
        // popoverElem = document.querySelector('.circle[data-bs-toggle="popover"]');
        // popoverElem.setAttribute("data-bs-content", currentProgress);
        popoverList[0].setContent({
          ".popover-body": currentProgress
        });
        // console.log(popoverElem);
        // updateStep();
      }
      else if (fastdna_progress){
        // parsed_progress = JSON.parse(fastdna_progress);
        progress_str = '';
        Object.keys(fastdna_progress).forEach((key) => {
          progress_str += `${key} ${fastdna_progress[key]}</br>`
        });
        console.log(progress_str);
        currentProgress = progress_str;
        popoverList[0].setContent({
          ".popover-body": currentProgress
        });
      }
      else if (response['status'] < 1){
        updateStep(response['status']);
      }

      if (response['run_info']['eval']) {
        // iterationData[`iter_${currentIter}`] = {'eval': response['run_info']['eval']};
        iterationData[`iter_${currentIter}`]['eval'] = response['run_info']['eval'];
        iterButton = document.getElementById(`button-iter_${currentIter}`);
        currentScore = parseFloat(response['run_info']['eval']['accordance']);
        if (currentScore <= bestScore){
          iterButton.innerHTML += `
          <span class="badge rounded-pill text-bg-primary badge-iter">${response['run_info']['eval']['accordance']}</span>
          `;
        }
        else {
          try {
            document.querySelector(".highest-badge").classList.remove('highest-badge');
          } catch (err){
              console.log(err);
          }
          iterButton.innerHTML += `
          <span class="badge rounded-pill text-bg-primary badge-iter highest-badge">${response['run_info']['eval']['accordance']}</span>
          `;
          bestScore = currentScore;
        }
      }

      if (response['run_info']['iter'])
      {
        if (!counterSet) {
          counter = response['run_info']['iter'] - 1;
          counterSet = true;
        }
        currentIter = response['run_info']['iter'];
        count();
        // iterationData[`iter_${currentIter}`] = {'hypers': response['run_info']['hypers']};
        iterationData[`iter_${currentIter}`]['hypers'] = response['run_info']['hypers'];
        console.log(iterationData);
        createIterationRecord(accordionIters, currentIter);
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


function copyToClipboard(elem) {
  var copyText = document.getElementById(elem);
  console.log(copyText);
  var button = document.querySelector('.btn-icon');

  // Disable the button
  button.disabled = true;
  // copyText.select();
  // copyText.setSelectionRange(0, 999999);

  navigator.clipboard.writeText(copyText.innerText);
  // alert("Copied the text: " + copyText.innerText);

  gsap.to(".bi-clipboard", {
      opacity: 0,
      duration: 0.18,
      ease: "expo.inOut"
  });
  gsap.to(".bi-clipboard-check", {
      opacity: 1,
      duration: 0.18,
      ease: "expo.inOut"
  });

  setTimeout(function() {
      gsap.to(".bi-clipboard", {
          opacity: 1,
          duration: 0.18,
          ease: "expo.inOut"
      });
      gsap.to(".bi-clipboard-check", {
          opacity: 0,
          duration: 0.18,
          ease: "expo.inOut"
      });

      // Enable the button
      button.disabled = false;
  }, 2000);
}

function createIterationRecord(container, iter_num) {
  record_id = `iter_${iter_num}`;
  record_html = `
  <div class="accordion-item">
    <h5 class="accordion-header">
        <button id="button-${record_id}" class="accordion-button accordion-button-iters collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#${record_id}" aria-expanded="false" aria-controls="${record_id}">
        Iteration ${iter_num}
        </button>
    </h5>
    <div id="${record_id}" class="accordion-collapse collapse">
        <div class="accordion-body">
          <div class="container-fluid" id="${record_id}-data">
            <h3 class="flavor fw-bold">No data yet.</h3>
          </div>
        </div>
    </div>
  </div>
  `;
  container.innerHTML += record_html;
}

accordionIters.addEventListener('show.bs.collapse', e => {
  console.log(e.target.id);
  console.log(iterationData[e.target.id]['hypers']);
  dataContainer = e.target.querySelector(`#${e.target.id}-data`);
  // console.log(dataContainer);

  // populate data
  dataHtml = '<h2 class="pb-2 border-bottom border-bottom-flavored flavor">Chosen hyperparameters</h2><div class="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4 g-4 py-2">';
  hypersData = iterationData[e.target.id]['hypers'];
  for (let key in hypersData) {
    dataHtml += `
    <div class="col d-flex align-items-start">
      <div>
        <h3 class="fw-bold mb-0 fs-4 flavor-5"> ${hypersData[key][0]} </h3>
        <p class="d-inline-flex lead flavor-5 console-font"> ${key}</p>
        <p class="flavor-visibility"> ${hypersData[key][1]} </p>
      </div>
    </div>
    `;
  }
  dataHtml += '</div>';
  console.log(dataHtml);
  try {
    evalData = iterationData[e.target.id]['eval'];
    dataHtml += `
    <h2 class="pb-2 border-bottom border-bottom-flavored flavor">Model evaluation</h2>
    <div class="row">
      <div class="d-flex justify-content-between flex-wrap">
    `;
    for (let key in evalData) {
      if (key != 'accordance') {
        dataHtml += `
        <div class="d-flex flex-column">
          <h3 class="flavor-5 fw-bold fs-4 capitalise"> ${key} %</h3>
          <p class="flavor-visibility">Top: ${evalData[key]['top']}</p>
          <p class="flavor-visibility">Top 3: ${evalData[key]['top3']}</p>
        </div>
        `;
      } else {
        dataHtml += `
        <div class="d-flex flex-column">
          <h3 class="flavor-5 fw-bold fs-4 capitalise"> ${key} </h3>
          <p class="flavor-visibility"> ${evalData[key]} </p>
        </div>
        `;
      }
    }
  } catch (err) {
    console.log(err);
  }
  dataContainer.innerHTML = dataHtml;
  console.log(dataContainer);

  badge = e.target.previousElementSibling.querySelector(".badge");
  gsap.to(badge, {
      opacity: 0,
      y: 100,
      duration: 0.3,
      ease: "power3.inOut"
  });
})

accordionIters.addEventListener('hide.bs.collapse', e => {
  badge = e.target.previousElementSibling.querySelector(".badge");
  gsap.to(badge, {
      opacity: 1,
      y: 0,
      duration: 0.3,
      ease: "power3.inOut"
  });
})

accordionIters.addEventListener('hidden.bs.collapse', e => {
  dataContainer = e.target.querySelector(`#${e.target.id}-data`);
  dataContainer.innerHTML = '';
})