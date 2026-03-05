export interface HVACPlugin {
  id: string;
  name: string;
  version: string;
  type: 'geometry' | 'export' | 'analysis' | 'ui';
  install: (registry: PluginRegistry) => void;
}

export class PluginRegistry {
  private plugins: Map<string, HVACPlugin> = new Map();

  register(plugin: HVACPlugin): void {
    if (this.plugins.has(plugin.id)) {
      console.warn(`[PluginRegistry] Plugin "${plugin.id}" is already registered and will be overwritten.`);
    }
    this.plugins.set(plugin.id, plugin);
    plugin.install(this);
  }

  unregister(id: string): void {
    this.plugins.delete(id);
  }

  getPlugin(id: string): HVACPlugin | undefined {
    return this.plugins.get(id);
  }

  listPlugins(): HVACPlugin[] {
    return Array.from(this.plugins.values());
  }
}

export const globalPluginRegistry = new PluginRegistry();
