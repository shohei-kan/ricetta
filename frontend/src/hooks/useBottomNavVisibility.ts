import { useEffect, useState } from 'react'

const MOBILE_MEDIA_QUERY = '(max-width: 767px)'
const TOP_VISIBLE_OFFSET = 24
const SCROLL_THRESHOLD = 24

export function useBottomNavVisibility(pathname: string) {
  const [isVisible, setIsVisible] = useState(true)

  useEffect(() => {
    const mediaQuery = window.matchMedia(MOBILE_MEDIA_QUERY)
    let lastScrollY = window.scrollY
    let scrollAnchorY = lastScrollY

    function resetVisibility() {
      lastScrollY = window.scrollY
      scrollAnchorY = lastScrollY
      setIsVisible(true)
    }

    function handleScroll() {
      if (!mediaQuery.matches) {
        return
      }

      const currentScrollY = Math.max(window.scrollY, 0)

      if (currentScrollY <= TOP_VISIBLE_OFFSET) {
        resetVisibility()
        return
      }

      const directionChanged =
        (currentScrollY > lastScrollY && scrollAnchorY > lastScrollY) ||
        (currentScrollY < lastScrollY && scrollAnchorY < lastScrollY)

      if (directionChanged) {
        scrollAnchorY = lastScrollY
      }

      if (currentScrollY - scrollAnchorY >= SCROLL_THRESHOLD) {
        setIsVisible(false)
        scrollAnchorY = currentScrollY
      } else if (scrollAnchorY - currentScrollY >= SCROLL_THRESHOLD) {
        setIsVisible(true)
        scrollAnchorY = currentScrollY
      }

      lastScrollY = currentScrollY
    }

    function handleBreakpointChange() {
      resetVisibility()
    }

    resetVisibility()
    window.addEventListener('scroll', handleScroll, { passive: true })
    mediaQuery.addEventListener('change', handleBreakpointChange)

    return () => {
      window.removeEventListener('scroll', handleScroll)
      mediaQuery.removeEventListener('change', handleBreakpointChange)
    }
  }, [pathname])

  return isVisible
}
