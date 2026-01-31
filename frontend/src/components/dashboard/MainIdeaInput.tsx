import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface MainIdeaInputProps {
  onSubmit: (prompt: string) => Promise<void>;
  isLoading?: boolean;
}

export function MainIdeaInput({ onSubmit, isLoading }: MainIdeaInputProps) {
  const [prompt, setPrompt] = useState('');

  const handleSubmit = async () => {
    if (!prompt.trim() || isLoading) return;
    await onSubmit(prompt.trim());
    setPrompt('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <Card className="border-primary/20 bg-card/50 backdrop-blur">
      <CardHeader>
        <CardTitle className="text-2xl">What do you want to build?</CardTitle>
        <CardDescription>
          Describe your web application idea. Our AI agents will design, build, and deploy it for you.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Textarea
          placeholder="Create a landing page for a SaaS product that helps teams collaborate on documents. Include a hero section, features grid, pricing table, and a contact form..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={handleKeyDown}
          className="min-h-[150px] resize-none"
          disabled={isLoading}
        />
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Press <kbd className="rounded bg-muted px-1.5 py-0.5 text-xs">Ctrl</kbd> +{' '}
            <kbd className="rounded bg-muted px-1.5 py-0.5 text-xs">Enter</kbd> to submit
          </p>
          <Button onClick={handleSubmit} disabled={!prompt.trim() || isLoading} size="lg">
            {isLoading ? 'Creating...' : 'Build My App'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
