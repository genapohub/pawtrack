/**
 * 通用 CSV 导出工具
 * 将表格数据导出为 CSV 文件下载
 */

export function exportCSV(filename: string, columns: { title: string; dataIndex: string }[], data: any[]) {
  // 表头
  const header = columns.map(c => `"${c.title}"`).join(',')
  // 数据行
  const rows = data.map(item =>
    columns.map(c => {
      const val = item[c.dataIndex] ?? ''
      // 转义双引号，包裹字段
      return `"${String(val).replace(/"/g, '""')}"`
    }).join(',')
  )
  // 加 BOM 防止 Excel 中文乱码
  const csv = '\uFEFF' + [header, ...rows].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename.endsWith('.csv') ? filename : `${filename}.csv`
  a.click()
  URL.revokeObjectURL(url)
}
