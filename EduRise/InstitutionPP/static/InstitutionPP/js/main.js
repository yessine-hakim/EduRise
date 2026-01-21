// EduRise - Enhanced JavaScript for animations and interactions

document.addEventListener("DOMContentLoaded", () => {
  initNavigation()
  initActiveLinks()
  initScrollAnimations()
  initSmoothScrolling()
  initFormEnhancements()
  initAccessibility()
})

// Navigation hamburger menu toggle
function initNavigation() {
  const hamburger = document.querySelector(".hamburger")
  const navMenu = document.querySelector(".nav-menu")

  if (hamburger) {
    hamburger.addEventListener("click", () => {
      navMenu.classList.toggle("active")

      // Animate hamburger
      const spans = hamburger.querySelectorAll("span")
      spans[0].style.transform = navMenu.classList.contains("active")
        ? "rotate(45deg) translate(8px, 8px)"
        : "rotate(0) translate(0, 0)"
      spans[1].style.opacity = navMenu.classList.contains("active") ? "0" : "1"
      spans[2].style.transform = navMenu.classList.contains("active")
        ? "rotate(-45deg) translate(7px, -7px)"
        : "rotate(0) translate(0, 0)"
    })

    // Close menu on link click
    const navLinks = navMenu.querySelectorAll(".nav-link")
    navLinks.forEach((link) => {
      link.addEventListener("click", () => {
        navMenu.classList.remove("active")
        const spans = hamburger.querySelectorAll("span")
        spans[0].style.transform = "rotate(0) translate(0, 0)"
        spans[1].style.opacity = "1"
        spans[2].style.transform = "rotate(0) translate(0, 0)"
      })
    })
  }
}

// Set active navigation link based on current URL
function initActiveLinks() {
  const navLinks = document.querySelectorAll(".nav-link")
  const currentUrl = window.location.pathname
  const currentFile = window.location.href.split("/").pop() || "index.html"

  navLinks.forEach((link) => {
    const href = link.getAttribute("href")

    // Check if current file matches link href
    if (currentFile === href || (currentFile === "" && href === "index.html")) {
      link.classList.add("active")
    } else {
      link.classList.remove("active")
    }
  })
}

// Smooth scroll behavior for anchor links
function initSmoothScrolling() {
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      const href = this.getAttribute("href")
      if (href !== "#" && href !== "") {
        e.preventDefault()
        const target = document.querySelector(href)
        if (target) {
          const offsetTop = target.offsetTop - 80
          window.scrollTo({
            top: offsetTop,
            behavior: "smooth",
          })
        }
      }
    })
  })
}

// Enhanced scroll animations with Intersection Observer
function initScrollAnimations() {
  // Check if user prefers reduced motion
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches

  if (prefersReducedMotion) {
    // Skip animations for users who prefer reduced motion
    document.querySelectorAll(".fade-in").forEach((el) => {
      el.classList.add("visible")
    })
    return
  }

  // Intersection Observer for fade-in animations
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible")
        observer.unobserve(entry.target)
      }
    })
  }, observerOptions)

  // Observe elements with fade-in class
  document.querySelectorAll(".fade-in").forEach((el) => {
    observer.observe(el)
  })

  // Observe cards for staggered animations
  const cards = document.querySelectorAll(".feature-card, .module-card, .stat-card, .output-card, .insight-item")
  cards.forEach((card, index) => {
    card.style.animationDelay = `${index * 0.1}s`
    observer.observe(card)
  })
}

// Form enhancements
function initFormEnhancements() {
  // Add floating label effect
  const formInputs = document.querySelectorAll(".form-group input, .form-group select")
  
  formInputs.forEach((input) => {
    // Add focus/blur effects
    input.addEventListener("focus", function() {
      this.parentElement.classList.add("focused")
    })
    
    input.addEventListener("blur", function() {
      this.parentElement.classList.remove("focused")
      if (this.value) {
        this.parentElement.classList.add("has-value")
      } else {
        this.parentElement.classList.remove("has-value")
      }
    })

    // Check initial value
    if (input.value) {
      input.parentElement.classList.add("has-value")
    }
  })

  // Form validation feedback
  const forms = document.querySelectorAll("form")
  forms.forEach((form) => {
    form.addEventListener("submit", function(e) {
      const inputs = form.querySelectorAll("input[required], select[required]")
      let isValid = true

      inputs.forEach((input) => {
        if (!input.value.trim()) {
          isValid = false
          input.classList.add("error")
          input.addEventListener("input", function() {
            this.classList.remove("error")
          }, { once: true })
        }
      })

      if (!isValid) {
        e.preventDefault()
        // Show error message
        const errorMsg = document.createElement("div")
        errorMsg.className = "error-message"
        errorMsg.textContent = "Please fill in all required fields."
        errorMsg.style.cssText = "margin-top: 1rem; padding: 1rem; background-color: #f8d7da; color: #721c24; border-radius: 6px;"
        
        const existingError = form.querySelector(".error-message")
        if (existingError) {
          existingError.remove()
        }
        form.appendChild(errorMsg)
        
        // Remove error message after 5 seconds
        setTimeout(() => {
          errorMsg.remove()
        }, 5000)
      }
    })
  })
}

// Accessibility enhancements
function initAccessibility() {
  // Keyboard navigation for cards
  const interactiveCards = document.querySelectorAll(".module-card, .feature-card")
  
  interactiveCards.forEach((card) => {
    const link = card.querySelector("a")
    if (link) {
      card.setAttribute("tabindex", "0")
      card.setAttribute("role", "button")
      
      card.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault()
          link.click()
        }
      })
    }
  })

  // Announce dynamic content changes to screen readers
  const messages = document.querySelectorAll(".message")
  messages.forEach((message) => {
    message.setAttribute("role", "alert")
    message.setAttribute("aria-live", "polite")
  })

  // Close message on Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      const messages = document.querySelectorAll(".message")
      messages.forEach((msg) => {
        const closeBtn = msg.querySelector(".message-close")
        if (closeBtn) {
          closeBtn.click()
        }
      })
    }
  })

  // Improve focus management for modals and overlays
  const sidebar = document.getElementById("sidebar")
  if (sidebar) {
    const sidebarToggle = document.getElementById("sidebarToggle")
    if (sidebarToggle) {
      sidebarToggle.addEventListener("click", () => {
        // Focus management for sidebar
        setTimeout(() => {
          if (!sidebar.classList.contains("collapsed")) {
            const firstNavItem = sidebar.querySelector(".nav-item")
            if (firstNavItem) {
              firstNavItem.focus()
            }
          }
        }, 300)
      })
    }
  }
}

// Utility function for debouncing
function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

// Optimized scroll handler with debouncing
const handleScroll = debounce(() => {
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop
  const header = document.querySelector(".navbar")
  
  if (header) {
    if (scrollTop > 50) {
      header.classList.add("scrolled")
    } else {
      header.classList.remove("scrolled")
    }
  }
}, 10)

window.addEventListener("scroll", handleScroll, { passive: true })

// Initialize on page load
window.addEventListener("load", () => {
  // Remove loading states if any
  document.body.classList.add("loaded")
  
  // Trigger initial animations
  initScrollAnimations()
})
 
