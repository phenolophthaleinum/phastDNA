
var atest = document.getElementById("ajax-test");
var spinner = document.getElementById("spinner");
var task_name = document.getElementById("task-name").innerText;
var page_title = document.getElementsByTagName('title').innerText;
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
      if (response['status'] === -1){
        gsap.to(".icon", {
          rotation: 0,
          duration: 0.5,
          ease: "power3.inOut",
        });
        gsap.to("#p2", {
          // rotation: -relRot,
          duration: 0.5,
          // delay: 3,
          strokeDashoffset: 0,
          attr: { d: "M 5 5 C 100 100 100 100 195 195" },
          filter: "drop-shadow(0px 0px 5px rgb(204, 69, 69))",
          stroke: "red",
          strokeWidth: 12,
          ease: "power3.inOut",
          onComplete: () => {
            gsap.set("#p2", {
              filter: "drop-shadow(0px 0px 5px rgb(204, 69, 69))"
            });
            gsap.to("#p2", {
              filter: "drop-shadow(0px 0px 5px rgb(204, 69, 69))",
              repeat: -1,
              yoyo: true,
              duration: 1,
              ease: "power1.inOut"
            });
          }
        });
        gsap.to("#p3", {
          // delay: 3,
          duration: 0.5,
          // rotation: -relRot,
          strokeDashoffset: 0,
          attr: { d: "M 195 5 C 100 100 100 100 5 195" },
          filter: "drop-shadow(0px 0px 5px rgb(204, 69, 69))",
          stroke: "red",
          strokeWidth: 12,
          ease: "power3.inOut",
          onComplete: () => {
            gsap.set("#p3", {
              filter: "drop-shadow(0px 0px 5px rgb(204, 69, 69))"
            });
            gsap.to("#p3", {
              filter: "drop-shadow(0px 0px 5px rgb(204, 69, 69))",
              repeat: -1,
              yoyo: true,
              duration: 1,
              ease: "power1.inOut"
            });
          }
        });
        gsap.to("#p4", {
          // delay: 3,
          opacity: 0,
          duration: 0.5,
          strokeDashoffset: 1,
          // attr: { d: "M 195 5 C 100 100 100 100 5 195" },
          // stroke: "red",
          strokeWidth: 12,
          ease: "power3.inOut",
        });
        gsap.to("#p1", {
          // delay: 3,
          opacity: 0,
          duration: 0.5,
          strokeDashoffset: 1,
          // attr: { d: "M 195 23 C 148 90 148 94 99 166" },
          // filter: "drop-shadow(0px 0px 5px rgb(102, 227, 143))",
          // stroke: "#66e38f",
          strokeWidth: 12,
          ease: "power3.inOut"
        });
        spinnerRotation.pause();
        pathAnim.pause();
        document.title = "phastDNA: task failed"
        clearInterval(interval);
      }
      if (response['status'] === 0){
        gsap.to(".icon", {
          rotation: 0,
          duration: 0.5,
          ease: "power3.inOut",
        });
        gsap.to("#p2", {
          // rotation: -relRot,
          duration: 0.5,
          // delay: 3,
          strokeDashoffset: 100,
          // attr: { d: "M 5 5 C 100 100 100 100 195 195" },
          // filter: "drop-shadow(0px 0px 5px rgb(204, 69, 69))",
          // stroke: "red",
          strokeWidth: 12,
          ease: "power3.inOut",
        });
        gsap.to("#p3", {
          // delay: 3,
          duration: 0.5,
          // rotation: -relRot,
          strokeDashoffset: 0,
          attr: { d: "M 35 96 C 60 123 60 123 99 166" },
          filter: "drop-shadow(0px 0px 5px rgb(102, 227, 143))",
          stroke: "#66e38f",
          strokeWidth: 12,
          ease: "power3.inOut",
          onComplete: () => {
            gsap.set("#p3", {
              filter: "drop-shadow(0px 0px 5px rgb(102, 227, 143))"
            });
            gsap.to("#p3", {
              filter: "drop-shadow(0px 0px 15px rgb(102, 227, 143))",
              repeat: -1,
              yoyo: true,
              duration: 1,
              ease: "power1.inOut"
            });
          }
        });
        gsap.to("#p4", {
          // delay: 3,
          // opacity: 0,
          duration: 0.5,
          strokeDashoffset: 100,
          // attr: { d: "M 195 5 C 100 100 100 100 5 195" },
          // stroke: "red",
          strokeWidth: 12,
          ease: "power3.inOut",
        });
        gsap.to("#p1", {
          // delay: 3,
          // opacity: 0,
          duration: 0.5,
          strokeDashoffset: 0,
          attr: { d: "M 195 23 C 148 90 148 94 99 166" },
          filter: "drop-shadow(0px 0px 5px rgb(102, 227, 143))",
          stroke: "#66e38f",
          strokeWidth: 12,
          ease: "power3.inOut",
          onComplete: () => {
            gsap.set("#p1", {
              filter: "drop-shadow(0px 0px 5px rgb(102, 227, 143))"
            });
            gsap.to("#p1", {
              filter: "drop-shadow(0px 0px 15px rgb(102, 227, 143))",
              repeat: -1,
              yoyo: true,
              duration: 1,
              ease: "power1.inOut"
            });
          }
        });
        spinnerRotation.pause();
        pathAnim.pause();
        document.title = "phastDNA: task successful"
        clearInterval(interval)
      }
      // atest.innerText = response['content'];
      if (response['status'] === 0){
        var normalPara = document.createElement("p");
        var successPara = document.createElement("p");
        successPara.classList.add("fade-in", "status-success");
        normalPara.classList.add("fade-in");
        response_split = response['content'].split('\n');
        successPara.innerText = response_split.at(-2);
        normalPara.innerText = response_split.slice(0, -2).join('\n');
        atest.appendChild(normalPara);
        atest.appendChild(successPara);
      }
      else if (response['status'] === -1){
        // var normalPara = document.createElement("p");
        var successPara = document.createElement("p");
        successPara.classList.add("fade-in", "status-error");
        // normalPara.classList.add("fade-in");
        // response_split = response['content'].split('\n');
        // successPara.innerText = response_split.at(-2);
        successPara.innerText = response['content'];
        // normalPara.innerText = response_split.slice(0, -2).join('\n');
        // atest.appendChild(normalPara);
        atest.appendChild(successPara);
      }
      else {
        console.log(response['content']);
        var para = document.createElement("p");
        para.innerText = response['content'];
        para.classList.add('fade-in');
        atest.appendChild(para);
      }
      // atest.innerHTML += `<p>${response['content']}</p><br>`;

    },
    error: function(xhr) {
        alert(xhr.responseText);
    }
  });
}, 2000);