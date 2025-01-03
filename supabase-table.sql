-- Create posts table
create table posts (
  id bigint primary key generated by default as identity,
  title text not null,
  image text,
  filename text unique,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()),
  metadata jsonb
);

-- Enable Row Level Security (RLS)
alter table posts enable row level security;

-- Create policy to allow public read access
create policy "Public posts are viewable by everyone" on posts
  for select using (true);

-- Create policy to allow authenticated users to insert
create policy "Authenticated users can insert posts" on posts
  for insert with check (auth.role() = 'authenticated');

-- Create policy to allow users to update their own posts
create policy "Users can update their own posts" on posts
  for update using (auth.uid() = user_id);