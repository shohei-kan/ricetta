import {
  forwardRef,
  useLayoutEffect,
  useRef,
  type ChangeEvent,
  type TextareaHTMLAttributes,
} from 'react'

type AutoResizeTextareaProps = TextareaHTMLAttributes<HTMLTextAreaElement> & {
  minRows?: number
}

export const AutoResizeTextarea = forwardRef<HTMLTextAreaElement, AutoResizeTextareaProps>(
  function AutoResizeTextarea(
    {
      className = '',
      defaultValue,
      minRows = 1,
      onChange,
      value,
      ...props
    },
    forwardedRef,
  ) {
    const textareaRef = useRef<HTMLTextAreaElement | null>(null)

    useLayoutEffect(() => {
      if (textareaRef.current) {
        resizeTextarea(textareaRef.current)
      }
    }, [defaultValue, minRows, value])

    function setRefs(element: HTMLTextAreaElement | null) {
      textareaRef.current = element

      if (typeof forwardedRef === 'function') {
        forwardedRef(element)
        return
      }

      if (forwardedRef) {
        forwardedRef.current = element
      }
    }

    function handleChange(event: ChangeEvent<HTMLTextAreaElement>) {
      resizeTextarea(event.currentTarget)
      onChange?.(event)
    }

    return (
      <textarea
        {...props}
        className={['resize-none overflow-hidden', className].filter(Boolean).join(' ')}
        defaultValue={defaultValue}
        onChange={handleChange}
        ref={setRefs}
        rows={minRows}
        value={value}
      />
    )
  },
)

function resizeTextarea(textarea: HTMLTextAreaElement) {
  textarea.style.height = 'auto'
  textarea.style.height = `${textarea.scrollHeight}px`
}
