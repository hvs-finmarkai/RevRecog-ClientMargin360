import { useState } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getPaginationRowModel,
  flexRender,
  ColumnDef,
  SortingState,
} from '@tanstack/react-table';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { ChevronUp, ChevronDown, ChevronsUpDown, ChevronLeft, ChevronRight } from 'lucide-react';

interface DataTableProps<T> {
  data: T[];
  columns: ColumnDef<T, unknown>[];
  isLoading?: boolean;
  emptyMessage?: string;
  onRowClick?: (row: T) => void;
  pageSize?: number;
  className?: string;
}

function DataTable<T>({ data, columns, isLoading = false, emptyMessage = 'No data available', onRowClick, pageSize = 10, className }: DataTableProps<T>) {
  const [sorting, setSorting] = useState<SortingState>([]);

  const table = useReactTable({
    data,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: { pagination: { pageSize } },
  });

  if (isLoading) {
    return (
      <div className={twMerge('bg-white rounded-xl border border-gray-200 overflow-hidden', className)}>
        <div className="animate-pulse">
          <div className="h-12 bg-gray-100 border-b border-gray-200" />
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-14 border-b border-gray-100 px-4 py-3">
              <div className="h-4 bg-gray-200 rounded w-3/4" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className={twMerge('bg-white rounded-xl border border-gray-200 p-12 text-center', className)}>
        <p className="text-gray-500 text-sm">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className={twMerge('bg-white rounded-xl border border-gray-200 overflow-hidden', className)}>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id} className="border-b border-gray-200 bg-gray-50">
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    className={clsx(
                      'px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider',
                      header.column.getCanSort() && 'cursor-pointer select-none hover:text-gray-900'
                    )}
                    onClick={header.column.getToggleSortingHandler()}
                  >
                    <div className="flex items-center gap-1.5">
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      {header.column.getCanSort() && (
                        <span className="text-gray-400">
                          {header.column.getIsSorted() === 'asc' ? (
                            <ChevronUp className="h-3.5 w-3.5" />
                          ) : header.column.getIsSorted() === 'desc' ? (
                            <ChevronDown className="h-3.5 w-3.5" />
                          ) : (
                            <ChevronsUpDown className="h-3.5 w-3.5" />
                          )}
                        </span>
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map((row) => (
              <tr
                key={row.id}
                onClick={() => onRowClick?.(row.original)}
                className={clsx(
                  'border-b border-gray-100 last:border-0 transition-colors',
                  onRowClick && 'cursor-pointer hover:bg-gray-50'
                )}
              >
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="px-4 py-3.5 text-sm text-gray-700">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {table.getPageCount() > 1 && (
        <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200">
          <p className="text-sm text-gray-500">
            Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
          </p>
          <div className="flex items-center gap-2">
            <button
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
              className="p-1.5 rounded-lg border border-gray-300 text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
              className="p-1.5 rounded-lg border border-gray-300 text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export { DataTable };
export type { DataTableProps };
