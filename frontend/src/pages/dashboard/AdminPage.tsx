import { useState, useEffect } from 'react';
import { Plus, X, Users } from 'lucide-react';
import apiClient from '@/lib/axios';
import { useAppStore } from '@/store/appStore';
import toast from 'react-hot-toast';

const roleOptions = ['viewer', 'analyst', 'finance_manager', 'admin'];

export default function AdminPage() {
  const { setPageTitle } = useAppStore();
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ email: '', first_name: '', last_name: '', password: '', password_confirm: '', role: 'analyst' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    setPageTitle('User Management');
    loadUsers();
  }, [setPageTitle]);

  async function loadUsers() {
    try {
      const res = await apiClient.get('/users/users/');
      setUsers(res.data?.results || res.data?.data || res.data || []);
    } catch {
      setUsers([]);
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (form.password !== form.password_confirm) {
      setError('Passwords do not match');
      return;
    }

    if (form.password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    try {
      const payload = {
        email: form.email,
        first_name: form.first_name,
        last_name: form.last_name,
        password: form.password,
        password_confirm: form.password_confirm,
        is_active: true,
      };
      await apiClient.post('/users/users/', payload);
      setSuccess(`User "${form.first_name} ${form.last_name}" created successfully! They can now log in.`);
      setForm({ email: '', first_name: '', last_name: '', password: '', password_confirm: '', role: 'analyst' });
      setShowForm(false);
      loadUsers();
      toast.success('User created successfully');
    } catch (err: any) {
      const errorData = err.response?.data;
      let detail = '';
      if (errorData) {
        if (typeof errorData === 'string') {
          detail = errorData;
        } else {
          const messages = Object.entries(errorData).map(([key, val]: [string, any]) => {
            const msg = Array.isArray(val) ? val.join(', ') : val;
            return `${key}: ${msg}`;
          });
          detail = messages.join(' | ');
        }
      }
      if (!detail) detail = 'Failed to create user';
      setError(detail);
      toast.error(detail);
    }
  }

  async function handleDelete(id: string, name: string) {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) return;

    try {
      await apiClient.delete(`/users/users/${id}/`);
      setSuccess(`User "${name}" deleted`);
      loadUsers();
      toast.success('User deleted');
    } catch {
      setError('Failed to delete user');
      toast.error('Failed to delete user');
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-navy-900 dark:text-[#F1F5F9]">User Management</h1>
          <p className="text-sm text-navy-500 dark:text-navy-300 mt-1">{users.length} users registered</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="btn-primary flex items-center gap-2"
        >
          {showForm ? <><X className="w-4 h-4" />Cancel</> : <><Plus className="w-4 h-4" />Add User</>}
        </button>
      </div>

      {success && (
        <div className="rounded-lg bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 p-3 text-sm text-emerald-700 dark:text-emerald-400">
          {success}
        </div>
      )}

      {error && (
        <div className="rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-3 text-sm text-red-700 dark:text-red-400">
          {error}
        </div>
      )}

      {showForm && (
        <div className="bg-white dark:bg-[#1E293B] rounded-xl border border-navy-100 dark:border-[#334155] shadow-card p-6">
          <h3 className="text-lg font-semibold text-navy-900 dark:text-[#F1F5F9] mb-4">Create New User</h3>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-navy-700 dark:text-navy-300">First Name *</label>
              <input
                value={form.first_name}
                onChange={(e) => setForm({ ...form, first_name: e.target.value })}
                className="mt-1 h-10 w-full rounded-lg border border-navy-200 dark:border-[#334155] bg-white dark:bg-[#0F172A] px-3 text-sm text-navy-900 dark:text-[#F1F5F9] focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>
            <div>
              <label className="text-sm font-medium text-navy-700 dark:text-navy-300">Last Name *</label>
              <input
                value={form.last_name}
                onChange={(e) => setForm({ ...form, last_name: e.target.value })}
                className="mt-1 h-10 w-full rounded-lg border border-navy-200 dark:border-[#334155] bg-white dark:bg-[#0F172A] px-3 text-sm text-navy-900 dark:text-[#F1F5F9] focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>
            <div>
              <label className="text-sm font-medium text-navy-700 dark:text-navy-300">Email *</label>
              <input
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                className="mt-1 h-10 w-full rounded-lg border border-navy-200 dark:border-[#334155] bg-white dark:bg-[#0F172A] px-3 text-sm text-navy-900 dark:text-[#F1F5F9] focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>
            <div>
              <label className="text-sm font-medium text-navy-700 dark:text-navy-300">Role</label>
              <select
                value={form.role}
                onChange={(e) => setForm({ ...form, role: e.target.value })}
                className="mt-1 h-10 w-full rounded-lg border border-navy-200 dark:border-[#334155] bg-white dark:bg-[#0F172A] px-3 text-sm text-navy-900 dark:text-[#F1F5F9] focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {roleOptions.map(r => <option key={r} value={r}>{r.replace('_', ' ')}</option>)}
              </select>
            </div>
            <div>
              <label className="text-sm font-medium text-navy-700 dark:text-navy-300">Password *</label>
              <input
                type="password"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                className="mt-1 h-10 w-full rounded-lg border border-navy-200 dark:border-[#334155] bg-white dark:bg-[#0F172A] px-3 text-sm text-navy-900 dark:text-[#F1F5F9] focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
                minLength={8}
                placeholder="Minimum 8 characters"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-navy-700 dark:text-navy-300">Confirm Password *</label>
              <input
                type="password"
                value={form.password_confirm}
                onChange={(e) => setForm({ ...form, password_confirm: e.target.value })}
                className="mt-1 h-10 w-full rounded-lg border border-navy-200 dark:border-[#334155] bg-white dark:bg-[#0F172A] px-3 text-sm text-navy-900 dark:text-[#F1F5F9] focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
                minLength={8}
                placeholder="Repeat password"
              />
            </div>
            <div className="md:col-span-2 flex justify-end">
              <button type="submit" className="btn-primary px-6">Create User</button>
            </div>
          </form>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-4 border-primary-200 border-t-primary-500 rounded-full animate-spin" />
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-navy-100 dark:border-[#334155] bg-white dark:bg-[#1E293B]">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-navy-50 dark:bg-[#0F172A] border-b border-navy-100 dark:border-[#334155]">
                <th className="py-3 px-4 text-left font-medium text-navy-500 dark:text-navy-300">Name</th>
                <th className="py-3 px-4 text-left font-medium text-navy-500 dark:text-navy-300">Email</th>
                <th className="py-3 px-4 text-left font-medium text-navy-500 dark:text-navy-300">Role</th>
                <th className="py-3 px-4 text-center font-medium text-navy-500 dark:text-navy-300">Status</th>
                <th className="py-3 px-4 text-left font-medium text-navy-500 dark:text-navy-300">Last Login</th>
                <th className="py-3 px-4 text-center font-medium text-navy-500 dark:text-navy-300">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user: any) => (
                <tr key={user.id} className="border-b border-navy-100 dark:border-[#334155] last:border-0 hover:bg-navy-50 dark:hover:bg-white/5">
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-3">
                      <div className="h-8 w-8 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center text-xs font-bold text-primary-600">
                        {(user.full_name || `${user.first_name} ${user.last_name}`).split(' ').map((n: string) => n[0]).join('').toUpperCase()}
                      </div>
                      <span className="font-medium text-navy-900 dark:text-[#F1F5F9]">{user.full_name || `${user.first_name} ${user.last_name}`}</span>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-navy-500 dark:text-navy-300">{user.email}</td>
                  <td className="py-3 px-4">
                    <span className="capitalize text-navy-700 dark:text-navy-200">{user.role_detail?.name || (user.is_staff ? 'Admin' : 'User')}</span>
                  </td>
                  <td className="py-3 px-4 text-center">
                    {user.is_active ? (
                      <span className="inline-flex items-center rounded-full bg-emerald-100 dark:bg-emerald-900/30 px-2.5 py-0.5 text-xs font-medium text-emerald-700 dark:text-emerald-400">Active</span>
                    ) : (
                      <span className="inline-flex items-center rounded-full bg-red-100 dark:bg-red-900/30 px-2.5 py-0.5 text-xs font-medium text-red-700 dark:text-red-400">Inactive</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-navy-500 dark:text-navy-300 text-xs">
                    {user.last_login ? new Date(user.last_login).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : '—'}
                  </td>
                  <td className="py-3 px-4 text-center">
                    <button
                      onClick={() => handleDelete(user.id, user.full_name || `${user.first_name} ${user.last_name}`)}
                      className="text-xs text-red-500 hover:text-red-700 font-medium"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
              {users.length === 0 && (
                <tr>
                  <td colSpan={6} className="py-12 text-center">
                    <Users className="w-12 h-12 text-navy-300 mx-auto mb-3" />
                    <p className="text-navy-500 dark:text-navy-300">No users found</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
