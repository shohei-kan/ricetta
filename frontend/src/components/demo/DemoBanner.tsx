import { isDemoMode } from '../../config/demo'

export function DemoBanner() {
  if (!isDemoMode) {
    return null
  }

  return (
    <div className="border-b border-[#e8d7c3] bg-[#fff4e8] px-4 py-2 text-center text-sm font-medium text-[#8a4b25] md:px-6">
      公開デモ環境です。入力内容は定期的に初期化されます。実店舗データではありません。
    </div>
  )
}
