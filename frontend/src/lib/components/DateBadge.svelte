<script lang="ts">
    import { format } from 'date-fns';
    let { date }: {date: Date} = $props(); 
    function formatDate(date: Date) {
        const now = new Date();
        const isSameYear = date.getFullYear() === now.getFullYear();
        return isSameYear
        ? format(date, 'MMMM, d')
        : format(date, 'MMMM, d, yyyy');
  }
</script>

<span class="text-sm self-center font-semibold my-2">{formatDate(date)}</span>