import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Plus, Trash2, Users, Shield, Building2, X } from 'lucide-react';
import apiClient from '@/lib/axios';
import { useAppStore } from '@/store/appStore';
import type { User, UserRole } from '@/types';
import toast from 'react-hot-toast';

const createUserSchema = z.object({
  email: z.string().email(),
  first_name: z.string().min(1),
  last_name: z.string().min(1),
  password: z.string().min(8),
  password_confirm: z.string().min(8),
  role: z.enum(['admin', 'finance_manager', 'analyst', 'viewer']),
}).refine((data) => data.password === data.password_confirm, {
  message: "Passwords don't match",
  path: ["password_confirm"],
});

type CreateUserForm = z.infer<typeof createUserSchema>;

const roles: { value: UserRole; label: string }[] = [
  { value: 'admin', label: 'Admin' },
  { value: 'finance_manager', label: 'Finance Manager' },
  { value: 'analyst', label: 'Analyst' },
  { value: 'viewer', label: 'Viewer' },
];

export default function AdminPage() {
  const { setPageTitle } = useAppStore();
  const queryClient = useQueryClient();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);

  useEffect(() => {
    setPageTitle('Admin');
  }, [setPageTitle]);

  const { data: users, isLoading, error } = useQuery<User[]>({
    queryKey: ['admin-users'],
    queryFn: async () => {
      const res = await apiClient.get('/users/users/');
      return res.data?.data || res.data || [];
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: CreateUserForm) => {
      const payload = {
        email: data.email,
        first_name: data.first_name,
        last_name: data.last_name,
        password: data.password,
        password_confirm: data.password_confirm,
        is_active: true,
      };
      return apiClient.post('/users/users/', payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
      setShowCreateModal(false);
      toast.success('User created successfully');
    },
    onError: () => {
      toast.error('Failed to create user');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => apiClient.delete(`/users/users/${id}/`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
      setDeleteConfirmId(null);
      toast.success('User deleted successfully');
    },
    onError: () => {
      toast.error('Failed to delete user');
    },
  });

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CreateUserForm>({
    resolver: zodResolver(createUserSchema),
    defaultValues: { role: 'analyst' },
  });

  const onSubmit = (data: CreateUserForm) => {
    createMutation.mutate(data);
  };

  const handleOpenCreate = () => {
    reset();
    setShowCreateModal(true);
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-navy-900 dark:text-[#F1F5F9]">Administration</h1>
          <p className="text-sm text-navy-500 dark:text-navy-300 mt-1">Manage users, roles, and organization settings</p>
        </div>
      </div>

      <section className="bg-white dark:bg-[#1E293B] rounded-xl border border-navy-100 dark:border-[#334155] shadow-card p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <Users className="w-5 h-5 text-primary-500" />
            <h2 className="text-lg font-semibold text-navy-900 dark:text-[#F1F5F9]">User Management</h2>
          </div>
          <button onClick={handleOpenCreate} className="btn-primary flex items-center gap-2">
            <Plus className="w-4 h-4" />
            <span>Create User</span>
          </button>
        </div>

        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <div className="w-8 h-8 border-4 border-primary-200 border-t-primary-500 rounded-full animate-spin" />
          </div>
        )}

        {error && (
          <div className="text-center py-12">
            <p className="text-danger-500">Failed to load users. Please try again.</p>
          </div>
        )}

        {!isLoading && !error && users && users.length === 0 && (
          <div className="text-center py-12">
            <Users className="w-12 h-12 text-navy-300 mx-auto mb-3" />
            <p className="text-navy-500 dark:text-navy-300">No users found</p>
          </div>
        )}

        {!isLoading && !error && users && users.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-navy-100 dark:border-[#334155]">
                  <th className="table-header dark:bg-[#0F172A] dark:text-navy-300">Email</th>
                  <th className="table-header dark:bg-[#0F172A] dark:text-navy-300">Name</th>
                  <th className="table-header dark:bg-[#0F172A] dark:text-navy-300">Role</th>
                  <th className="table-header dark:bg-[#0F172A] dark:text-navy-300">Status</th>
                  <th className="table-header dark:bg-[#0F172A] dark:text-navy-300">Last Login</th>
                  <th className="table-header dark:bg-[#0F172A] dark:text-navy-300">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-navy-100 dark:divide-[#334155]">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-navy-50 dark:hover:bg-white/5">
                    <td className="table-cell dark:text-[#F1F5F9]">{u.email}</td>
                    <td className="table-cell dark:text-[#F1F5F9]">{u.name}</td>
                    <td className="table-cell">
                      <span className="badge-primary">{u.role.replace('_', ' ')}</span>
                    </td>
                    <td className="table-cell">
                      {u.isActive ? (
                        <span className="badge-success">Active</span>
                      ) : (
                        <span className="badge-danger">Inactive</span>
                      )}
                    </td>
                    <td className="table-cell dark:text-navy-300">
                      {u.lastLogin ? new Date(u.lastLogin).toLocaleDateString() : '—'}
                    </td>
                    <td className="table-cell">
                      {deleteConfirmId === u.id ? (
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => deleteMutation.mutate(u.id)}
                            disabled={deleteMutation.isPending}
                            className="text-xs px-2 py-1 bg-danger-500 text-white rounded hover:bg-danger-600 transition-colors"
                          >
                            Confirm
                          </button>
                          <button
                            onClick={() => setDeleteConfirmId(null)}
                            className="text-xs px-2 py-1 bg-navy-200 dark:bg-navy-600 text-navy-700 dark:text-navy-200 rounded hover:bg-navy-300 dark:hover:bg-navy-500 transition-colors"
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => setDeleteConfirmId(u.id)}
                          className="text-danger-500 hover:text-danger-700 transition-colors p-1"
                          aria-label="Delete user"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="bg-white dark:bg-[#1E293B] rounded-xl border border-navy-100 dark:border-[#334155] shadow-card p-6">
        <div className="flex items-center gap-2 mb-6">
          <Shield className="w-5 h-5 text-primary-500" />
          <h2 className="text-lg font-semibold text-navy-900 dark:text-[#F1F5F9]">Role Management</h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {roles.map((role) => (
            <div
              key={role.value}
              className="p-4 rounded-lg border border-navy-100 dark:border-[#334155] bg-navy-50 dark:bg-[#0F172A]"
            >
              <p className="font-medium text-navy-900 dark:text-[#F1F5F9]">{role.label}</p>
              <p className="text-xs text-navy-500 dark:text-navy-300 mt-1">{role.value}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="bg-white dark:bg-[#1E293B] rounded-xl border border-navy-100 dark:border-[#334155] shadow-card p-6">
        <div className="flex items-center gap-2 mb-6">
          <Building2 className="w-5 h-5 text-primary-500" />
          <h2 className="text-lg font-semibold text-navy-900 dark:text-[#F1F5F9]">Organization Settings</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="label dark:text-navy-300">Organization Name</label>
            <input type="text" defaultValue="Finmark.ai" className="input-field dark:bg-[#0F172A] dark:border-[#334155] dark:text-[#F1F5F9]" readOnly />
          </div>
          <div>
            <label className="label dark:text-navy-300">Primary Domain</label>
            <input type="text" defaultValue="finmark.ai" className="input-field dark:bg-[#0F172A] dark:border-[#334155] dark:text-[#F1F5F9]" readOnly />
          </div>
          <div>
            <label className="label dark:text-navy-300">Default Currency</label>
            <input type="text" defaultValue="INR" className="input-field dark:bg-[#0F172A] dark:border-[#334155] dark:text-[#F1F5F9]" readOnly />
          </div>
          <div>
            <label className="label dark:text-navy-300">Fiscal Year Start</label>
            <input type="text" defaultValue="April" className="input-field dark:bg-[#0F172A] dark:border-[#334155] dark:text-[#F1F5F9]" readOnly />
          </div>
        </div>
      </section>

      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="fixed inset-0 bg-black/50" onClick={() => setShowCreateModal(false)} />
          <div className="relative bg-white dark:bg-[#1E293B] rounded-xl shadow-xl w-full max-w-md p-6 border border-navy-100 dark:border-[#334155]">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-navy-900 dark:text-[#F1F5F9]">Create User</h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-navy-400 hover:text-navy-600 dark:hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div>
                <label className="label dark:text-navy-300">Email</label>
                <input
                  type="email"
                  {...register('email')}
                  className={`input-field dark:bg-[#0F172A] dark:border-[#334155] dark:text-[#F1F5F9] ${errors.email ? 'input-error' : ''}`}
                  placeholder="user@company.com"
                />
                {errors.email && <p className="text-xs text-danger-500 mt-1">{errors.email.message}</p>}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label dark:text-navy-300">First Name</label>
                  <input
                    type="text"
                    {...register('first_name')}
                    className={`input-field dark:bg-[#0F172A] dark:border-[#334155] dark:text-[#F1F5F9] ${errors.first_name ? 'input-error' : ''}`}
                  />
                  {errors.first_name && <p className="text-xs text-danger-500 mt-1">{errors.first_name.message}</p>}
                </div>
                <div>
                  <label className="label dark:text-navy-300">Last Name</label>
                  <input
                    type="text"
                    {...register('last_name')}
                    className={`input-field dark:bg-[#0F172A] dark:border-[#334155] dark:text-[#F1F5F9] ${errors.last_name ? 'input-error' : ''}`}
                  />
                  {errors.last_name && <p className="text-xs text-danger-500 mt-1">{errors.last_name.message}</p>}
                </div>
              </div>

              <div>
                <label className="label dark:text-navy-300">Password</label>
                <input
                  type="password"
                  {...register('password')}
                  className={`input-field dark:bg-[#0F172A] dark:border-[#334155] dark:text-[#F1F5F9] ${errors.password ? 'input-error' : ''}`}
                  placeholder="Minimum 8 characters"
                />
                {errors.password && <p className="text-xs text-danger-500 mt-1">{errors.password.message}</p>}
              </div>

              <div>
                <label className="label dark:text-navy-300">Confirm Password</label>
                <input
                  type="password"
                  {...register('password_confirm')}
                  className={`input-field dark:bg-[#0F172A] dark:border-[#334155] dark:text-[#F1F5F9] ${errors.password_confirm ? 'input-error' : ''}`}
                  placeholder="Repeat password"
                />
                {errors.password_confirm && <p className="text-xs text-danger-500 mt-1">{errors.password_confirm.message}</p>}
              </div>

              <div>
                <label className="label dark:text-navy-300">Role</label>
                <select
                  {...register('role')}
                  className={`input-field dark:bg-[#0F172A] dark:border-[#334155] dark:text-[#F1F5F9] ${errors.role ? 'input-error' : ''}`}
                >
                  {roles.map((r) => (
                    <option key={r.value} value={r.value}>{r.label}</option>
                  ))}
                </select>
                {errors.role && <p className="text-xs text-danger-500 mt-1">{errors.role.message}</p>}
              </div>

              <div className="flex items-center justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="btn-secondary dark:bg-[#0F172A] dark:border-[#334155] dark:text-[#F1F5F9] dark:hover:bg-[#334155]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createMutation.isPending}
                  className="btn-primary"
                >
                  {createMutation.isPending ? 'Creating...' : 'Create User'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
