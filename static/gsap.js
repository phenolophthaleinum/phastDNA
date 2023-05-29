gsap.from(".nav-item", 0.25, {
    opacity: 0, 
    y: 60,
    // yoyo: true, 
    // repeat: -1, 
    // ease: "power1.inOut",
    delay: 0,
    ease: "power1.inOut", 
    force3D: true,
    stagger: {
      amount: 0.1, 
    //   grid: "auto",
    //   from: "center"
    }
  })